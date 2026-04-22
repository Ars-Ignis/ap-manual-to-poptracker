ScriptHost:LoadScript("scripts/archipelago/item_mapping.lua")
ScriptHost:LoadScript("scripts/archipelago/location_mapping.lua")

CUR_INDEX = -1
SLOT_DATA = nil
HINT_DATASTORAGE_KEY = nil

if Highlight then --checking to see if we're on a version of PopTracker that has highlighting
    HIGHLIGHT_TABLE = {
        [0] = Highlight.Unspecified,
        [10] = Highlight.NoPriority,
        [20] = Highlight.Avoid,
        [30] = Highlight.Priority,
        [40] = Highlight.None,
    }
end


function onDataStorageUpdate(key, value, oldValue)
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(string.format("called onDataStorageUpdate with params key: %s, value: %s, oldValue: %s", key, value, oldValue))
    end
    if key == HINT_DATASTORAGE_KEY and value ~= oldValue then
        for k, hint in pairs(value) do
            if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
                print(string.format("table value: key: %s, value: %s", k, hint))
                for hint_key, hint_value in pairs(hint) do
                    print(string.format("hint value: key: %s, value: %s", hint_key, hint_value))
                end
            end
            if hint["finding_player"] == Archipelago.PlayerNumber then
                local hinted_location = Tracker:FindObjectForCode(ID_TO_LOCATION_MAP[hint["location"]][1])
                hinted_location.Highlight = HIGHLIGHT_TABLE[hint["status"]]
            end
        end
    end
end

function onClear(slot_data)
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print("called onClear, slot_data:\n")
        if slot_data ~= nil then
            for k, v in pairs(slot_data) do
                print(string.format("%s: %s", k, v))
            end
        else
            print("nil\n")
        end
    end
    CUR_INDEX = -1
    SLOT_DATA = slot_data
    if SLOT_DATA ~= nil then
        for key, value in pairs(SLOT_DATA) do
            local flag_obj = Tracker:FindObjectForCode(key)
            if flag_obj ~= nil then
                if flag_obj.Type == "toggle" then
                    flag_obj.Active = (value ~= 0)
                elseif flag_obj.Type == "consumable" then
                    flag_obj.AcquiredCount = value
                elseif flag_obj.Type == "progressive" then
                    flag_obj.CurrentStage = STAGE_MAPPINGS[key][value]
                end
            end
        end
    end
    -- reset locations
    for _, v in pairs(ID_TO_LOCATION_MAP) do
        if v[1] then
            if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
                print(string.format("onClear: clearing location %s", v[1]))
            end
            local obj = Tracker:FindObjectForCode(v[1])
            if obj then
                if v[1]:sub(1, 1) == "@" then
                    obj.AvailableChestCount = obj.ChestCount
                else
                    obj.Active = false
                end
                obj.Highlight = Highlight.None
            elseif AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
                print(string.format("onClear: could not find object for code %s", v[1]))
            end
        end
    end
    -- reset items
    for _, v in pairs(ITEM_MAPPING) do
        if v[1] and v[2] then
            if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
                print(string.format("onClear: clearing item %s of type %s", v[1], v[2]))
            end
            local obj = Tracker:FindObjectForCode(v[1])
            if obj then
                if v[2] == "toggle" then
                    obj.Active = false
                elseif v[2] == "progressive" then
                    obj.CurrentStage = 0
                    obj.Active = false
                elseif v[2] == "consumable" then
                    obj.AcquiredCount = 0
                elseif AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
                    print(string.format("onClear: unknown item type %s for code %s", v[2], v[1]))
                end
            elseif AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
                print(string.format("onClear: could not find object for code %s", v[1]))
            end
        end
    end

    if Archipelago.PlayerNumber > -1 and Highlight then
        HINT_DATASTORAGE_KEY = "_read_hints_" .. Archipelago.TeamNumber .. "_" .. Archipelago.PlayerNumber
        if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
            print(string.format("onClear: datastorage hint key %s", HINT_DATASTORAGE_KEY))
        end
        Archipelago:SetNotify({HINT_DATASTORAGE_KEY})
        Archipelago:Get({HINT_DATASTORAGE_KEY})
    else
        HINT_DATASTORAGE_KEY = ""
    end
end

-- called when an item gets collected
function onItem(index, item_id, item_name, player_number)
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(string.format("called onItem: %s, %s, %s, %s, %s", index, item_id, item_name, player_number, CUR_INDEX))
    end
    if index <= CUR_INDEX then
        return
    end
    CUR_INDEX = index;
    local v = ITEM_MAPPING[item_id]
    if not v then
        if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
            print(string.format("onItem: could not find item mapping for id %s", item_id))
        end
        return
    end
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(string.format("onItem: code: %s, type %s", v[1], v[2]))
    end
    if not v[1] then
        return
    end
    local item_code = v[1]
    local item_type = v[2]
    local obj = Tracker:FindObjectForCode(item_code)
    if obj then
        if item_type == "toggle" then
            obj.Active = true
        elseif item_type == "progressive" then
            if obj.Active then
                obj.CurrentStage = obj.CurrentStage + 1
            else
                obj.Active = true
            end
        elseif item_type == "consumable" then
            obj.AcquiredCount = obj.AcquiredCount + obj.Increment
        elseif AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
            print(string.format("onItem: unknown item type %s for code %s", item_type, item_code))
        end
    elseif AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(string.format("onItem: could not find object for code %s", v[1]))
    end
end

--called when a location gets cleared
function onLocation(location_id, location_name)
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(string.format("called onLocation: %s, %s", location_id, location_name))
    end
    local codes = ID_TO_LOCATION_MAP[location_id]
    if not codes and AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(string.format("onLocation: could not find location mapping for id %s", location_id))
    end
    for _, code in pairs(codes) do
        if not code then
            return
        end
        local obj = Tracker:FindObjectForCode(code)
        if obj then
            if code:sub(1, 1) == "@" then
                obj.AvailableChestCount = obj.AvailableChestCount - 1
            else
                obj.Active = true
            end
        elseif AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
            print(string.format("onLocation: could not find object for code %s", code))
        end
    end
end

-- called when a locations is scouted
function onScout(location_id, location_name, item_id, item_name, item_player)
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(string.format("called onScout: %s, %s, %s, %s, %s", location_id, location_name, item_id, item_name,
            item_player))
    end
end

-- called when a bounce message is received 
function onBounce(json)
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(string.format("called onBounce: %s", json))
    end
end

function onLocationSectionChanged(section)
    local sectionID = section.FullID
	if (section.AvailableChestCount == 0) then
        local apID = LOCATION_TO_ID_MAP[sectionID]
        if apID ~= nil then
            local res = Archipelago:LocationChecks({apID})
            if res then
                print("Sent " .. tostring(apID) .. " for " .. tostring(sectionID))
            else
                print("Error sending " .. tostring(apID) .. " for " .. tostring(sectionID))
            end
        else
            print(tostring(sectionID) .. " is not an AP location")
        end
    end
end

ScriptHost:AddOnLocationSectionChangedHandler("manual", onLocationSectionChanged)

-- add AP callbacks
-- un-/comment as needed
Archipelago:AddClearHandler("clear handler", onClear)
Archipelago:AddItemHandler("item handler", onItem)
Archipelago:AddLocationHandler("location handler", onLocation)
Archipelago:AddSetReplyHandler("datastorage update handler", onDataStorageUpdate)
Archipelago:AddRetrievedHandler("datastorage update handler", onDataStorageUpdate)
-- Archipelago:AddScoutHandler("scout handler", onScout)
-- Archipelago:AddBouncedHandler("bounce handler", onBounce)
