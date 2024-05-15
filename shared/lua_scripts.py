pop_item_from_list_then_add_to_sorted_set_with_timestamp = """
local list_name = KEYS[1]
local sorted_set_name = KEYS[2]

local item = redis.call('LPOP', list_name)
if item then
    redis.call('ZADD', sorted_set_name, ARGV[1], item)
end

return item
"""

add_item_to_sorted_set_with_timestamp = """
local sorted_set_name = KEYS[1]

redis.call('ZADD', sorted_set_name, ARGV[1], ARGV[2])

return item
"""


pop_old_items_from_sorted_set_then_add_to_list = """
local sorted_set_name = KEYS[1]
local list_name = KEYS[2]

local items = redis.call('ZRANGEBYSCORE', sorted_set_name, '-inf',  ARGV[1])
if #items > 0 then
    for _, item in ipairs(items) do
        redis.call('ZREM', sorted_set_name, item)
        redis.call('LPUSH', list_name, item)
    end
end

return items
"""
