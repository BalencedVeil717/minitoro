const retries = 2;
const allowed_states = ["ok", "stale", "no_data"];


function get_message(state, last_state, err = null) {
	switch (state) {
		case "api_down":
			return `## Alert!!! \n### The API isn't responding. \n\`\`\`\n${err}\n\`\`\``;
		case "stale":
			return "## Error!! \n### The agent has been inactive for more than 3 minutes.";
		case "unknown":
			return "## Error!! \n### The API responded with an unexpected status."
		case "no_data":
			return "## Warning! \n### The API has no metrics data.";
		case "ok":
			if (last_state === "stale") {
				return "### The agent is sending data again.";
			} else if (last_state === "api_down") {
				return "### The API is up and running."
			}
			return "### The agent is alive and working."
		default:
			return "### No info about API."
	}
}

async function fetch_api_state(api_url) {
	const response = await fetch(api_url, {method: "GET", signal: AbortSignal.timeout(5000)});
	if (!response.ok) {
		throw new Error(`Error fetching lastcall: ${response.status} ${response.statusText}`);
	}
	const data = await response.json();
	if (!allowed_states.includes(data.status)) {
		return "unknown";
	} else {
		return data.status;
	}
}

async function sleep(time) {
	return new Promise((resolve) => setTimeout(resolve, time));
}

export default {
	async scheduled(controller, env, ctx) {
		let api_state = "unknown";
		let last_state = null;
		let send_alert = false;

		console.log("cron processed");
		try {
			last_state = await env.state.get("last_state");
		} catch (e) {
			last_state = null;
			console.error(`Error fetching last_state: ${e}`);
		}
		let i = 1;
		let error = null;
		while (i <= retries) {
			console.log(`Attempt : ${i}`);
			try {
				api_state = await fetch_api_state(env.API_URL);
				break;
			} catch (e) {
				api_state = "api_down"
				error = e;
				console.error(`Error fetching lastcall: ${e}`);
			}
			i++;
			if (i <= retries) {
				await sleep(5000)
			}
		}
		if (api_state === "ok" && last_state == null) {
			try {
				await env.state.put("last_state", "ok");
			} catch (e) {
				console.error(`Error updating last_state: ${e}`);
			}
			send_alert = false;
		} else if (!(api_state === last_state)) {
			send_alert = true;
		}

		console.log(`API State: ${api_state}`);
		if (send_alert) {
			let message_content = {
				"content": get_message(api_state, last_state, error)
			};
			try {
				const webhook_response = await fetch(env.WEBHOOK_URL, {
					method: "POST",
					headers: {
						"Content-Type": "application/json"
					},
					body: JSON.stringify(message_content)
				});

				if (!webhook_response.ok) {
					throw new Error(`Discord webhook error: ${webhook_response.status} ${webhook_response.statusText}`);
				}

				try {
					await env.state.put("last_state", api_state);
				} catch (e) {
					console.error(`Error updating last_state: ${e}`);
				}
			} catch (e) {
				console.error(e);
			}
		}
		try {
			await fetch(env.HEALTHCHECKS_URL,{method: "GET", signal: AbortSignal.timeout(5000)});
		} catch (e) {
			console.error(`Error pinging HEALTHCHECKS_URL: ${e}`);
		}
	},
	async fetch(request, env, ctx) {
		return new Response("Hello Nova!");
	}
	,
}
;
