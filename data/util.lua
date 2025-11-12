-- Check to see if a relevant flag is set to "off"
function negate(code)
	return Tracker:ProviderCountForCode(code) == 0
end

-- Returns true if there are at least count number of items from group group_name
function has_count_from_group(group_name, count)
    local group_members = ITEM_GROUPS[group_name]
    if group_members == nil then
        return false
    end
    local found_count = 0
    for _, item in pairs(group_members) do
        found_count = found_count + Tracker:ProviderCountForCode(item)
        if found_count >= tonumber(count) then
            return true
        end
    end
    return false
end

-- Below are logic functions that come bundled with Manual.
function ItemValue(value_category_name, target_value)
    category_values = ITEM_VALUES[value_category_name]
    if category_values == nil then
        return false
    end
    local current_value = 0
    for item_name, item_value in pairs(category_values) do
        local item_count = Tracker:ProviderCountForCode(item_name)
        current_value = current_value + (item_count * item_value)
        if current_value >= target_value then
            return true
        end
    end
    return false
end
