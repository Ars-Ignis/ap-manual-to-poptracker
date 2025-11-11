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
