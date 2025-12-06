; Script de Inno Setup para BMC Chatbot
; Crea un instalador profesional para Windows

#define MyAppName "BMC Chatbot"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "BMC Uruguay"
#define MyAppURL "https://www.bmc.com.uy"
#define MyAppExeName "BMC_Chatbot.exe"

[Setup]
; Información básica
AppId={{BMC_Chatbot_2024}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=dist
OutputBaseFilename=BMC_Chatbot_Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

; Idioma
DefaultUserInfoName=
DefaultUserInfoOrg=

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\BMC_Chatbot.exe"; DestDir: "{app}"; Flags: ignoreversion
; Incluir archivos adicionales si los hay
; Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
; Source: "matriz_precios.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := 'Bienvenido al instalador de BMC Chatbot';
  WizardForm.WelcomeLabel2.Caption := 'Este asistente te guiará en la instalación del chatbot de cotizaciones de BMC Uruguay.';
end;

