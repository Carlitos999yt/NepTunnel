-- =========================================================================
--  NepTunnel - Dynamic Player Name Synchronization Script (Roblox Studio)
--  Place this script in ServerScriptService inside your Roblox Place (.rbxl)
-- =========================================================================

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

local BRIDGE_URL = "http://127.0.0.1:7878/identity"

-- Helper function to fetch configured identity from NepTunnel Local Bridge
local function fetchNepIdentity()
    local success, responseText = pcall(function()
        return HttpService:GetAsync(BRIDGE_URL)
    end)

    if success and responseText then
        local decodeSuccess, data = pcall(function()
            return HttpService:JSONDecode(responseText)
        end)

        if decodeSuccess and data and data.name and data.name ~= "" then
            return data.name
        end
    end
    return nil
end

-- Helper function to apply custom DisplayName & 3D Overhead Name Tag
local function applyNepName(player, customName)
    if not customName or customName == "" then return end

    -- 1. Apply DisplayName to Player Instance (Leaderboard / Player List)
    pcall(function()
        player.DisplayName = customName
    end)

    -- 2. Apply DisplayName & 3D Overhead Tag to Character Humanoid
    local function onCharacterAdded(character)
        local humanoid = character:WaitForChild("Humanoid", 10)
        if humanoid then
            pcall(function()
                humanoid.DisplayName = customName
            end)
        end
    end

    if player.Character then
        onCharacterAdded(player.Character)
    end
    player.CharacterAdded:Connect(onCharacterAdded)
end

-- Synchronize Name when a Player joins the session
Players.PlayerAdded:Connect(function(player)
    task.spawn(function()
        local customName = fetchNepIdentity()
        if customName then
            applyNepName(player, customName)
            print("[NepTunnel] Synchronized DisplayName for " .. player.Name .. " -> " .. customName)
        end
    end)
end)

-- Process any existing players in the session
for _, player in ipairs(Players:GetPlayers()) do
    task.spawn(function()
        local customName = fetchNepIdentity()
        if customName then
            applyNepName(player, customName)
        end
    end)
end

print("[NepTunnel] NepNameSyncScript initialized successfully!")
