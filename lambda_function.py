import json
import boto3
import random

# --- Amazon Bedrock Client ---
bedrock_runtime = boto3.client(service_name='bedrock-runtime')

# --- Mock data for agent and map information ---
# (Expand this significantly with more detailed data)
agents_data = {
    "Jett": {
        "role": "Duelist",
        "abilities": ["Cloudburst", "Updraft", "Tailwind", "Blade Storm"],
        "strengths": ["Mobility", "Entry Fragger", "Space Creation"],
        "weaknesses": ["Fragile", "Reliant on Aim"],
        "tips": [
            "Use Cloudburst to create one-way smokes or escape tight situations.",
            "Combine Updraft and Tailwind for aggressive pushes and high-ground takes.",
            "Blade Storm is devastating in close-quarters but requires precise aim."
        ],
        # Add more map-specific tips for each agent
        "map_tips": {
            "Bind": ["Use Updraft to reach the top of Hookah quickly.", "Use Tailwind to dash through teleporters for unexpected flanks."],
            "Haven": ["Use Cloudburst to block vision on long angles like Garage to A Long.", "Updraft to Heaven is a powerful position."],
            # ... tips for other maps ...
        }
    },
    "Sage": {
        "role": "Sentinel",
        "abilities": ["Healing Orb", "Slow Orb", "Barrier Orb", "Resurrection"],
        "strengths": ["Healing", "Support", "Area Denial"],
        "weaknesses": ["Limited offensive capabilities", "Reliant on team positioning"],
        "tips": [
            "Prioritize healing teammates who are actively engaging in fights.",
            "Use Slow Orb to slow down enemy pushes or prevent rushes.", 
            "Barrier Orb can create safe spaces for planting or defending.",
            "Resurrection is a powerful ability, use it wisely to bring back key teammates."
        ],
        "map_tips": {
            "Bind": ["Use Barrier Orb to block off chokepoints like Hookah entrance.", "Resurrection can be used to revive teammates in safe spots like B Site."],
            "Haven": ["Wall off long angles with Barrier Orb (e.g., Garage to A Long).", "Use Slow Orb to control chokepoints like A Short."],
            # ... tips for other maps ...
        }
    },
    # ... Add data for other agents ...
}

maps_data = {
    "Bind": {
        "characteristics": ["Two teleporters", "Tight chokepoints", "Close-quarters combat"],
        "common_strategies": ["Early aggression", "Teleporter flanks", "Control of Hookah/U-Hall"],
        "attack_tips": [
            "Utilize teleporters for quick rotations and flanks.",
            "Coordinate pushes with smokes and flashes to take control of key areas like Hookah and Showers."
        ],
        "defense_tips": [
            "Play for information and control chokepoints with Sentinels or Controllers.", 
            "Watch for flanks through teleporters and use utility to delay pushes."
        ]
    }, 
    "Haven": {
        "characteristics": ["Three bomb sites", "Long sightlines", "Mix of open and closed areas"],
        "common_strategies": ["Split pushes", "Aggressive rotations", "Control of mid"],
        "attack_tips": [
            "Coordinate attacks on multiple sites to divide the enemy's attention.",
            "Use smokes to create cover and execute onto sites.", 
            "Gain control of mid to enable easier rotations."
        ],
        "defense_tips": [
            "Use Sentinels to watch flanks and delay pushes.", 
            "Communicate effectively to quickly rotate between sites.", 
            "Utilize utility to deny enemy control of key areas like Garage and Mid Window."
        ]
    },
    # ... add data for other maps ...
}

def lambda_handler(event, context):
    print(event)

    def get_named_parameter(event, name):
        return next((item for item in event['parameters'] if item['name'] == name), None).get('value')

    def call_bedrock(prompt):
        try:
            response = bedrock_runtime.invoke_model(
                modelId="anthropic.claude-v2",  
                accept="application/json",
                contentType="application/json",
                body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 200, "temperature": 0.5})
            )
            response_body = json.loads(response.get('body').read())
            return response_body.get("completion")
        except Exception as e:
            return f"Error calling Bedrock: {str(e)}"

    # --- Example functions for VALORANT_EDGE ---
    def get_agent_info(event):
        agent_name = get_named_parameter(event, 'agentName')
        if agent_name and agent_name.capitalize() in agents_data:
            return agents_data[agent_name.capitalize()]
        else:
            return {"error": "Agent not found or invalid input"} 

    def get_map_info(event):
        map_name = get_named_parameter(event, 'mapName')
        if map_name and map_name.capitalize() in maps_data:
            return maps_data[map_name.capitalize()]
        else:
            return {"error": "Map not found or invalid input"}

    def generate_pistol_round_strat(event):
        map_name = get_named_parameter(event, 'mapName') 

        if not map_name:
            return {"error": "Map name is required."}

        prompt = f"""
        Generate a VALORANT pistol round strategy for the {map_name} map. 
        Focus on early map control and common attack/defense strategies.
        """ 

        bedrock_response = call_bedrock(prompt)
        return bedrock_response

    def analyze_match_replay(event):
        # This function would require access to match replay data
        # You would need to use the VALORANT API or a third-party service 
        # to get and process replay data.
        replay_data = get_named_parameter(event, 'replayData')  # Placeholder 

        # ... (Logic to analyze replay data using Bedrock or custom models) ...

        analysis = "Match replay analysis is not yet implemented. Please provide replay data." 
        return analysis 

    def recommend_agent(event):
        map_name = get_named_parameter(event, 'mapName')
        player_role = get_named_parameter(event, 'playerRole')
        team_comp = get_named_parameter(event, 'teamComp') 

        # ... (Logic to suggest an agent using Bedrock, data, and potentially custom models) ...
        prompt = f"""
        Recommend a VALORANT agent for a player on the {map_name} map.
        Player Role: {player_role}
        Current Team Comp: {team_comp}
        Consider agent strengths, weaknesses, and map-specific strategies.
        """
        agent_recommendation = call_bedrock(prompt)
        return agent_recommendation


    # --- Add more VALORANT_EDGE functions as needed ---
    
    result = ''
    response_code = 200
    action_group = event.get('actionGroup')
    api_path = event.get('apiPath')
    
    print("api_path: ", api_path)
    
    if api_path == '/getAgentInfo':
        result = get_agent_info(event)
    elif api_path == '/getMapInfo':
        result = get_map_info(event)
    elif api_path == '/generatePistolRoundStrat':
        result = generate_pistol_round_strat(event)
    elif api_path == '/analyzeMatchReplay':
        result = analyze_match_replay(event)
    elif api_path == '/recommendAgent':
        result = recommend_agent(event)
    else:
        response_code = 404
        result = f"Unrecognized api path: {action_group}::{api_path}"
        
    response_body = {
        'application/json': {
            'body': result
        }
    }
        
    action_response = {
        'actionGroup': event.get('actionGroup'),
        'apiPath': event.get('apiPath'),
        'httpMethod': event.get('httpMethod'),
        'httpStatusCode': response_code,
        'responseBody': response_body
    }

    api_response = {'messageVersion': '1.0', 'response': action_response}
    return api_response
