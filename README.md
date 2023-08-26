# Creating BadUSB with $0?
REDTEECON 1 Conference Talk (18th August 2023)
- Researchers
  - Jordan Irshaad Zheng Yu Amin
  - Gerbelle Lim Zi Xuan

## Overview of Research
BadUSB is a security vulnerability and attack method that targets USB devices, including thumb drives, keyboards, and other USB peripherals. Malicious actions are executed on compromised systems by exploiting the inherent trust and functionality of USB devices. This research aims to explore the creation of a BadUSB device with a minimal budget of $0. 
Our study enables us to comprehend and investigate various attack techniques applicable to standard USBs. Furthermore, we aim to develop our own version of BadUSB, capable of executing malicious actions with user interaction. By understanding the mechanisms of BadUSB attacks, the research contributes to better safeguarding systems against potential breaches and encourages cybersecurity awareness and the importance of regularly updating and monitoring USB device interaction.

## Additional sub topics
- BadUSB attack with mimikatz using powershell script
- the output of mimikatz commands are stored in a file called mimikatz_output.txt 
- security measures in window 10
  - autorun is disabled
  - user account control promt
  - window denfender(real-time montitoring)
  - execution policy in powershell
- coverting powershell into an executable(exe) 
- social engineering to make the malicious exe enticing to click
- malicious folder cotaning the scripts in the USB drive is hidden and encrypted
  


## References/Links
https://www.varonis.com/blog/what-is-mimikatz 
https://www.avg.com/en/signal/how-to-password-protect-file-folder-in-windows 
https://github.com/FuzzySecurity/PowerShell-Suite/blob/master/Bypass-UAC/Bypass-UAC.ps1 
https://github.com/ParrotSec/mimikatz 
https://github.com/MScholtes/PS2EXE/blob/master/Win-PS2EXE/README.md
https://www.snapfiles.com/downloads/wbpassview/dlwbpassview.html 
https://techcaption.com/create-hacking-pendrive/
https://www.youtube.com/watch?v=DrKLebGeFpQ)https://www.youtube.com/watch?v=DrKLebGeFpQ
https://www.netspi.com/blog/technical/network-penetration-testing/15-ways-to-bypass-the-powershell-execution-policy/ 
https://www.microsoft.com/en-us/wdsi/definitions/antimalware-definition-release-notes?requestVersion=1.393.2528.0 
https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/microsoft-defender-antivirus-updates?view=o365-worldwide 
https://www.manageengine.com/data-security/security-threats/usb-drop-attack.html#:~:text=A%20USB%20drop%20attack%20occurs,to%20carry%20out%20their%20attacks.
