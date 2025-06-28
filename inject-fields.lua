local static_data = {
    user_id = "abc123"
    user_name = "Jane"
    client_ip = "192.168.1.10"
    user_agent = "Mozilla/5.0"
}

function inject(tag, ts, record)
    for k, v in pairs(static_data) do
        record[k] = v
    end
    return 1, ts, record
end

