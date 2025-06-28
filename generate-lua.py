import json

def flatten_and_map(data):
    result = {}

    # user.id -> user_id
    if 'user' in data:
        user = data['user']
        if 'id' in user:
            result['user_id'] = user['id']
        if 'name' in user:
            result['user_name'] = user['name']

    # request.ip -> client_ip
    if 'request' in data:
        request = data['request']
        if 'ip' in request:
            result['client_ip'] = request['ip']
        if 'user_agent' in request:
            result['user_agent'] = request['user_agent']

    return result

def to_lua_table(d):
    lines = []
    for k, v in d.items():
        # Quote strings properly for Lua
        v_str = v.replace('"', '\\"') if isinstance(v, str) else str(v)
        lines.append(f'    {k} = "{v_str}"')
    return "{\n" + "\n".join(lines) + "\n}"

def generate_lua_script(json_data):
    # Flatten and map keys from json_data['data']
    flat_data = flatten_and_map(json_data.get('data', {}))
    lua_table = to_lua_table(flat_data)

    lua_script = f"""local static_data = {lua_table}

function inject(tag, ts, record)
    for k, v in pairs(static_data) do
        record[k] = v
    end
    return 1, ts, record
end
"""
    return lua_script

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} input.json")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        json_data = json.load(f)

    lua_script = generate_lua_script(json_data)
    print(lua_script)

