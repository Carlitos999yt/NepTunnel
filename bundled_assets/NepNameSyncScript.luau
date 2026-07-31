-- =========================================================================
--  NepTunnel - Dynamic Player Name Synchronization & Leaderboard Overrider
--  Place this script in ServerScriptService inside your Roblox Place (.rbxl)
-- =========================================================================

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local StarterGui = game:GetService("StarterGui")

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

-- TÉCNICA #1: Apply DisplayName to Character Humanoid
local function applyHumanoidName(player, customName)
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

-- TÉCNICA #3: Create Custom Leaderboard UI with Name & Minutes Column
local function createCustomLeaderboard(player, customName)
    local playerGui = player:WaitForChild("PlayerGui", 10)
    if not playerGui then return end

    -- Disable Roblox Default PlayerList
    pcall(function()
        StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false)
    end)

    local existing = playerGui:FindFirstChild("NepCustomLeaderboard")
    if existing then existing:Destroy() end

    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "NepCustomLeaderboard"
    screenGui.ResetOnSpawn = false

    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(0, 220, 0, 110)
    frame.Position = UDim2.new(1, -230, 0, 10)
    frame.BackgroundColor3 = Color3.fromRGB(15, 15, 20)
    frame.BackgroundTransparency = 0.2
    frame.BorderSizePixel = 0
    frame.Parent = screenGui

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = frame

    -- Column Headers: Personas | Minutes
    local headerName = Instance.new("TextLabel")
    headerName.Size = UDim2.new(0.65, 0, 0, 30)
    headerName.Position = UDim2.new(0, 10, 0, 2)
    headerName.BackgroundTransparency = 1
    headerName.Text = "Personas"
    headerName.TextColor3 = Color3.fromRGB(200, 200, 200)
    headerName.Font = Enum.Font.SourceSansBold
    headerName.TextSize = 14
    headerName.TextXAlignment = Enum.TextXAlignment.Left
    headerName.Parent = frame

    local headerMin = Instance.new("TextLabel")
    headerMin.Size = UDim2.new(0.35, -10, 0, 30)
    headerMin.Position = UDim2.new(0.65, 0, 0, 2)
    headerMin.BackgroundTransparency = 1
    headerMin.Text = "Minutes"
    headerMin.TextColor3 = Color3.fromRGB(200, 200, 200)
    headerMin.Font = Enum.Font.SourceSansBold
    headerMin.TextSize = 14
    headerMin.TextXAlignment = Enum.TextXAlignment.Right
    headerMin.Parent = frame

    -- Divider line
    local div = Instance.new("Frame")
    div.Size = UDim2.new(1, -20, 0, 1)
    div.Position = UDim2.new(0, 10, 0, 32)
    div.BackgroundColor3 = Color3.fromRGB(60, 60, 80)
    div.BorderSizePixel = 0
    div.Parent = frame

    -- Player Row Frame
    local playerRow = Instance.new("Frame")
    playerRow.Size = UDim2.new(1, -20, 0, 28)
    playerRow.Position = UDim2.new(0, 10, 0, 38)
    playerRow.BackgroundTransparency = 1
    playerRow.Parent = frame

    local nameLabel = Instance.new("TextLabel")
    nameLabel.Size = UDim2.new(0.65, 0, 1, 0)
    nameLabel.Position = UDim2.new(0, 0, 0, 0)
    nameLabel.BackgroundTransparency = 1
    nameLabel.Text = "● " .. customName
    nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    nameLabel.Font = Enum.Font.SourceSansSemibold
    nameLabel.TextSize = 15
    nameLabel.TextXAlignment = Enum.TextXAlignment.Left
    nameLabel.Parent = playerRow

    local valLabel = Instance.new("TextLabel")
    valLabel.Size = UDim2.new(0.35, 0, 1, 0)
    valLabel.Position = UDim2.new(0.65, 0, 0, 0)
    valLabel.BackgroundTransparency = 1
    valLabel.Text = "0"
    valLabel.TextColor3 = Color3.fromRGB(220, 220, 220)
    valLabel.Font = Enum.Font.SourceSans
    valLabel.TextSize = 15
    valLabel.TextXAlignment = Enum.TextXAlignment.Right
    valLabel.Parent = playerRow

    -- Connect to player's leaderstats (Minutes counter)
    local function connectLeaderstats()
        local ls = player:FindFirstChild("leaderstats") or player:WaitForChild("leaderstats", 8)
        if ls then
            local function hookValue(statObj)
                if statObj then
                    valLabel.Text = tostring(statObj.Value)
                    statObj.Changed:Connect(function(newVal)
                        valLabel.Text = tostring(newVal)
                    end)
                end
            end

            local mins = ls:FindFirstChild("Minutes") or ls:FindFirstChildOfClass("IntValue") or ls:FindFirstChildOfClass("NumberValue")
            if mins then
                hookValue(mins)
            else
                ls.ChildAdded:Connect(function(child)
                    if child.Name == "Minutes" or child:IsA("IntValue") or child:IsA("NumberValue") then
                        hookValue(child)
                    end
                end)
            end
        end
    end

    task.spawn(connectLeaderstats)
    screenGui.Parent = playerGui
end

-- Process All Players
local function handlePlayer(player)
    task.spawn(function()
        local customName = fetchNepIdentity() or player.Name
        applyHumanoidName(player, customName)
        createCustomLeaderboard(player, customName)
    end)
end

Players.PlayerAdded:Connect(handlePlayer)
for _, player in ipairs(Players:GetPlayers()) do
    handlePlayer(player)
end

print("[NepTunnel] NepNameSyncScript (Custom Leaderboard + Minutes) loaded successfully!")
