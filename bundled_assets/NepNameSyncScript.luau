-- =========================================================================
--  NepTunnel - Dynamic Player Name Synchronization Script (Roblox Studio)
--  Place this script in ServerScriptService inside your Roblox Place (.rbxl)
-- =========================================================================

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- Enable HTTP Requests automatically in Roblox Studio local mode
pcall(function()
    HttpService.HttpEnabled = true
end)

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

-- Helper function to create/update 3D Overhead BillboardGui
local function attachOverheadTag(character, customName)
    local head = character:WaitForChild("Head", 10)
    if not head then return end

    -- Remove existing tag if present
    local existing = head:FindFirstChild("NepOverheadTag")
    if existing then existing:Destroy() end

    local bb = Instance.new("BillboardGui")
    bb.Name = "NepOverheadTag"
    bb.Adornee = head
    bb.Size = UDim2.new(0, 200, 0, 50)
    bb.StudsOffset = Vector3.new(0, 2.5, 0)
    bb.AlwaysOnTop = true

    local txt = Instance.new("TextLabel")
    txt.Size = UDim2.new(1, 0, 1, 0)
    txt.BackgroundTransparency = 1
    txt.Text = customName
    txt.TextColor3 = Color3.fromRGB(255, 255, 255)
    txt.TextStrokeColor3 = Color3.fromRGB(0, 0, 0)
    txt.TextStrokeTransparency = 0
    txt.Font = Enum.Font.SourceSansBold
    txt.TextSize = 22
    txt.Parent = bb

    bb.Parent = head
end

-- Helper function to apply custom DisplayName & 3D Overhead Name Tag
local function applyNepName(player, customName)
    if not customName or customName == "" then return end

    -- 1. Apply DisplayName to Player Instance (Leaderboard / Player List)
    pcall(function()
        player.DisplayName = customName
    end)

    -- 2. Apply DisplayName & 3D Overhead Tag to Character Humanoid & Head
    local function onCharacterAdded(character)
        local humanoid = character:WaitForChild("Humanoid", 10)
        if humanoid then
            pcall(function()
                humanoid.DisplayName = customName
            end)
        end
        attachOverheadTag(character, customName)
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
            print("[NepTunnel] Synchronized name for " .. player.Name .. " -> " .. customName)
        else
            print("[NepTunnel] No custom name provided, keeping default " .. player.Name)
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
