-- =========================================================================
--  NepTunnel - Client Leaderboard UI & TAB Key Handler
--  Colocar este LocalScript en: StarterGui (o StarterPlayerScripts)
-- =========================================================================

local Players = game:GetService("Players")
local StarterGui = game:GetService("StarterGui")
local UserInputService = game:GetService("UserInputService")

local localPlayer = Players.LocalPlayer

-- Desactivar la lista nativa de Roblox desde el cliente
pcall(function()
    StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false)
end)

local function buildLeaderboard()
    local playerGui = localPlayer:WaitForChild("PlayerGui")

    local existing = playerGui:FindFirstChild("NepCustomLeaderboard")
    if existing then existing:Destroy() end

    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "NepCustomLeaderboard"
    screenGui.ResetOnSpawn = false

    local frame = Instance.new("Frame")
    frame.Name = "LeaderboardFrame"
    frame.Size = UDim2.new(0, 220, 0, 110)
    frame.Position = UDim2.new(1, -230, 0, 10)
    frame.BackgroundColor3 = Color3.fromRGB(15, 15, 20)
    frame.BackgroundTransparency = 0.25
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

    -- Divider
    local div = Instance.new("Frame")
    div.Size = UDim2.new(1, -20, 0, 1)
    div.Position = UDim2.new(0, 10, 0, 32)
    div.BackgroundColor3 = Color3.fromRGB(60, 60, 80)
    div.BorderSizePixel = 0
    div.Parent = frame

    -- Rows Container
    local container = Instance.new("Frame")
    container.Name = "RowsContainer"
    container.Size = UDim2.new(1, -20, 1, -36)
    container.Position = UDim2.new(0, 10, 0, 34)
    container.BackgroundTransparency = 1
    container.Parent = frame

    local function updateList()
        container:ClearAllChildren()
        local yOffset = 0
        local nameCounts = {}

        for _, plr in ipairs(Players:GetPlayers()) do
            local row = Instance.new("Frame")
            row.Size = UDim2.new(1, 0, 0, 24)
            row.Position = UDim2.new(0, 0, 0, yOffset)
            row.BackgroundTransparency = 1
            row.Parent = container

            local customVal = plr:FindFirstChild("NepCustomName")
            local rawName = (customVal and customVal.Value ~= "") and customVal.Value or plr.DisplayName
            
            nameCounts[rawName] = (nameCounts[rawName] or 0) + 1
            local finalDisplay = rawName
            if nameCounts[rawName] > 1 then
                finalDisplay = rawName .. " (" .. tostring(nameCounts[rawName]) .. ")"
            end

            local nameLbl = Instance.new("TextLabel")
            nameLbl.Size = UDim2.new(0.65, 0, 1, 0)
            nameLbl.BackgroundTransparency = 1
            nameLbl.Text = "● " .. finalDisplay
            nameLbl.TextColor3 = Color3.fromRGB(255, 255, 255)
            nameLbl.Font = Enum.Font.SourceSansSemibold
            nameLbl.TextSize = 15
            nameLbl.TextXAlignment = Enum.TextXAlignment.Left
            nameLbl.Parent = row

            local valLbl = Instance.new("TextLabel")
            valLbl.Size = UDim2.new(0.35, 0, 1, 0)
            valLbl.Position = UDim2.new(0.65, 0, 0, 0)
            valLbl.BackgroundTransparency = 1
            valLbl.Text = "0"
            valLbl.TextColor3 = Color3.fromRGB(220, 220, 220)
            valLbl.Font = Enum.Font.SourceSans
            valLbl.TextSize = 15
            valLbl.TextXAlignment = Enum.TextXAlignment.Right
            valLbl.Parent = row

            local function hookLeaderstats()
                local ls = plr:FindFirstChild("leaderstats") or plr:WaitForChild("leaderstats", 5)
                if ls then
                    local mins = ls:FindFirstChild("Minutes") or ls:FindFirstChildOfClass("IntValue") or ls:FindFirstChildOfClass("NumberValue")
                    if mins then
                        valLbl.Text = tostring(mins.Value)
                        mins.Changed:Connect(function(v) valLbl.Text = tostring(v) end)
                    end
                end
            end
            task.spawn(hookLeaderstats)

            yOffset = yOffset + 26
        end

        frame.Size = UDim2.new(0, 220, 0, math.max(65, 42 + yOffset))
    end

    -- Update automatically when players join or leave
    Players.PlayerAdded:Connect(updateList)
    Players.PlayerRemoving:Connect(updateList)
    updateList()

    -- TAB Key Toggle Listener
    UserInputService.InputBegan:Connect(function(input, gameProcessed)
        if input.KeyCode == Enum.KeyCode.Tab then
            frame.Visible = not frame.Visible
        end
    end)

    screenGui.Parent = playerGui
end

task.spawn(buildLeaderboard)
print("[NepTunnel] Client Leaderboard UI initialized!")
