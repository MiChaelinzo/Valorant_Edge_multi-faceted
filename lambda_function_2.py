import json
import boto3 # For Amazon Bedrock 

# --- Mock data for agent and map information ---
agents_data = {
    "Jett": {
        "role": "Duelist",
        "abilities": ["Cloudburst", "Updraft", "Tailwind", "Blade Storm"],
        "strengths": ["Mobility", "Entry Fragger", "Space Creation"],
        "weaknesses": ["Fragile", "Reliant on Aim"],
    },
    "Sage": {
        # ... add data for other agents ...
    }
}

maps_data = {
    "Bind": {
        "characteristics": ["Two teleporters", "Tight chokepoints", "Close-quarters combat"],
        "common_strategies": ["Early aggression", "Teleporter flanks", "Control of Hookah/U-Hall"],
    }, 
    "Haven": {
        # ... add data for other maps ...
    }
}

def lambda_handler(event, context):
    print(event)

    def get_named_parameter(event, name):
        return next(item for item in event['parameters'] if item['name'] == name)['value']

    # --- Example functions for VALORANT_EDGE ---
    def get_agent_info(event):
        agent_name = get_named_parameter(event, 'agentName').capitalize()
        if agent_name in agents_data:
            return agents_data[agent_name]
        else:
            return {"error": "Agent not found"} 

    def get_map_info(event):
        map_name = get_named_parameter(event, 'mapName').capitalize()
        if map_name in maps_data:
            return maps_data[map_name]
        else:
            return {"error": "Map not found"}

    def generate_pistol_round_strat(event):
        map_name = get_named_parameter(event, 'mapName').capitalize() 

        # Example prompt for Amazon Bedrock - use actual API call
        prompt = f"""
        Generate a VALORANT pistol round strategy for the {map_name} map. 
        Focus on early map control and common attack/defense strategies.
        """ 

        # --- Replace with your Bedrock API call ---
        bedrock_response = call_bedrock(prompt) # You'll need to implement this 

        return bedrock_response

    # --- Add more VALORANT_EDGE functions as needed ---
    
    result = ''
    response_code = 200
    action_group = event['actionGroup']
    api_path = event['apiPath']
    
    print("api_path: ", api_path )
    
    if api_path == '/getAgentInfo':
        result = get_agent_info(event)
    elif api_path == '/getMapInfo':
        result = get_map_info(event)
    elif api_path == '/generatePistolRoundStrat':
        result = generate_pistol_round_strat(event)
    else:
        response_code = 404
        result = f"Unrecognized api path: {action_group}::{api_path}"
        
    response_body = {
        'application/json': {
            'body': result
        }
    }
        
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': response_code,
        'responseBody': response_body
    }

    api_response = {'messageVersion': '1.0', 'response': action_response}
    return api_response
