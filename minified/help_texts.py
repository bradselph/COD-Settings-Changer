def get_help_texts():return{'VideoMemoryScale':"Set a target fraction of your PC's video memory to be used by the game. Higher values may improve texture quality but could cause instability.",'RendererWorkerCount':'Sets the number of CPU threads for handling rendering tasks. Higher values may improve performance on multi-core CPUs.','VoicePushToTalk':'When enabled, you need to press a key to activate your microphone in voice chat.','AudioMix':'Selects from predefined audio mix presets for different listening environments.','Volume':'Adjusts the overall game volume.','VoiceVolume':'Adjusts the volume of character dialogues and announcer voices.','MusicVolume':'Adjusts the volume of background music.','EffectsVolume':'Adjusts the volume of sound effects.','HitMarkersVolume':'Adjusts the volume of hit marker sounds.','CapFps':'Enables or disables the custom frame rate limit.','MaxFpsInGame':'Sets the maximum frame rate during gameplay. Higher values provide smoother gameplay but require more powerful hardware.','MaxFpsInMenu':'Sets the maximum frame rate in menus. Lower values can reduce power consumption when not in gameplay.','MaxFpsOutOfFocus':'Sets the maximum frame rate when the game window is not in focus. Lower values can reduce resource usage when tabbed out.','DepthOfField':'Adds a blur effect to out-of-focus areas when aiming down sights. May impact performance.','DisplayMode':'Chooses between fullscreen, windowed, and borderless window modes.','NvidiaReflex':"Reduces system latency on NVIDIA GPUs. 'Enabled + boost' mode may provide the lowest latency but could increase power consumption.",'ParticleQualityLevel':'Adjusts the detail level of particle effects. Higher quality may impact performance in busy scenes.','DLSSMode':'Enables NVIDIA DLSS (Deep Learning Super Sampling) for improved performance at higher resolutions on supported GPUs.','AMDFidelityFX':'Enables AMD FidelityFX features for improved image quality or performance on supported GPUs.','HDR':'Enables High Dynamic Range for improved color and brightness on supported displays.','RecommendedSet':'Indicates whether recommended settings have been applied. If set to false, the game will reset settings to recommended values.','ShowBlood':'Toggles the display of blood effects in the game.','ShowBrass':'Toggles whether weapons eject brass (shell casings) when fired.','VSyncInMenu':'Enables vertical sync in menus to prevent screen tearing.','ResolutionMultiplier':'Adjusts the rendering resolution relative to the display resolution. Values below 100 can improve performance at the cost of image quality.','AspectRatio':"Forces a specific aspect ratio for the game, independent of the window's aspect ratio.",'FocusedMode':'Enables a mode that reduces on-screen distractions for better focus during gameplay.','TextureFilter':'Sets the quality of texture filtering. Higher values provide sharper textures at oblique angles but may impact performance.','Tessellation':'Controls the level of geometric detail. Higher values provide more detailed surfaces but impact performance.','VolumetricQuality':'Adjusts the quality of volumetric lighting effects. Higher quality provides more realistic fog and smoke but impacts performance.','SSAOTechnique':'Sets the method used for Screen Space Ambient Occlusion, which adds depth and realism to shadows in corners and crevices.','DLSSFrameGeneration':'Enables NVIDIA DLSS Frame Generation, which can significantly boost FPS on supported hardware.','FSRFrameInterpolation':'Enables AMD FSR Frame Interpolation, which can boost FPS on supported hardware.','ShaderQuality':'Adjusts the complexity and detail of shader effects. Lower settings can improve performance on older hardware.','DeferredPhysics':'Controls the quality of physics simulations. Higher quality provides more realistic physics but impacts CPU performance.','GPUUploadHeaps':'Enables optimizations for systems that support resizable BAR, allowing more efficient data transfer to the GPU.','MicrophoneVolume':'Adjusts the volume of your microphone input.','MicThreshold':'Sets the minimum volume threshold for your microphone to activate.','Brightness':'Adjusts the overall brightness of the game. Higher values make the game brighter but may wash out some details.','Fov':'Adjusts the Field of View in first-person perspective. Higher values show more of the game world but may cause distortion at the edges.','ThirdPersonFov':'Adjusts the Field of View in third-person perspective.','ADSFovScaling':'When enabled, maintains your set FOV when aiming down sights.','MouseInvertPitch':'Inverts the vertical mouse movement. Enable if you prefer pushing the mouse forward to look down.','MouseHorizontalSensibility':'Adjusts the horizontal sensitivity of the mouse. Higher values make camera movement more responsive.','MouseVerticalSensibility':'Adjusts the vertical sensitivity of the mouse. Higher values make camera movement more responsive.','ADSSensitivity':'Adjusts mouse sensitivity when aiming down sights. Lower values can help with precision aiming.','ConfigCloudStorageEnabled':'Enables cloud storage for your configuration settings.','ConfigCloudSavegameEnabled':'Enables cloud storage for your savegames.','EnableHUD':'Toggles the visibility of the Heads-Up Display (HUD) during gameplay.','FreeLook':"Enables the ability to look around freely without changing your character's direction of movement.",'MonoSound':'Enables mono audio output, which can be useful for players with hearing impairments or using a single earphone.','VoiceChat':'Enables or disables voice chat functionality in the game.','MouseAcceleration':'Applies acceleration to mouse movement. Higher values make the cursor move faster as you move the mouse quicker.','MouseFilter':'Applies smoothing to mouse movement. Higher values can reduce jitter but may introduce input lag.','MouseSmoothing':'Enables additional smoothing of mouse movement, which can reduce jitter but may introduce input lag.','ConstrainMouse':'When enabled, locks the mouse cursor to the game window.','HDRGamma':'Adjusts the gamma curve for HDR displays. Only applies when HDR is enabled.','HDRMaxLum':'Sets the maximum luminance for HDR content. Only applies when HDR is enabled.','HDRMinLum':'Sets the minimum luminance for HDR content. Only applies when HDR is enabled.','TextureQuality':'Adjusts the resolution of textures. Lower numbers indicate higher quality. Higher quality requires more VRAM and may impact performance.','AudioWantedChannelsNumber':'Sets the number of audio output channels. Valid values are 2, 4, 6, 8, 16. Zero uses system default.','CinematicVolume':'Adjusts the volume of audio during cinematic sequences.','MuteAudioWhileOutOfFocus':'Mutes game audio when the window is not in focus.','LicensedMusicVolume':'Adjusts the volume of licensed music in the game.','WarTracksVolume':'Adjusts the volume of war tracks in the game.','TelescopeVolume':'Adjusts the volume of audio in the Telescope (Message of the Day) feature.','MicInactivityMuteDelay':'Sets the delay (in seconds) before muting the microphone due to inactivity. Set to -1 to disable.','MicRecLevel':'Adjusts the recording level of your microphone.','MicThresholdAggressive':'Sets an aggressive threshold for microphone activation. Used in conjunction with voice_mic_threshold.','MicThresholdLoud':'Sets the threshold for detecting loud talking. Used in conjunction with voice_mic_threshold.','MicAggressiveInTime':'Sets the duration of continuous talk time before switching to aggressive voice threshold.','MicAggressiveOutTime':'Sets the duration of continuous mute time before switching back to normal voice threshold.','MicPostLoudAggressiveTime':'Sets the duration to use aggressive threshold after detecting loud talking to prevent audio feedback.','WindowsSonicEnable':"Enables Microsoft's Windows Sonic 3D audio spatializer. When disabled, presents a standard 7.1 mix.",'MicNormalTimeOut':'Sets the duration of silence before cutting the microphone after normal talking.','MicLoudTimeOut':'Sets the duration of silence before cutting the microphone after loud talking.','CorpseLimit':'Sets the maximum number of AI corpses that can appear in the game.','BloodLimit':'Enables limiting of blood effects to prevent excessive accumulation.','BloodLimitInterval':'Sets the interval (in milliseconds) between blood effects when blood limiting is enabled.','MarksEntsPlayerOnly':"When enabled, only the player's bullets will leave marks on entities.",'InvalidCmdHintDuration':'Sets the duration (in milliseconds) for which invalid command hints are displayed.','InvalidCmdHintBlinkInterval':'Sets the blink rate (in milliseconds) for invalid command hints.','MapLocationSelectionCursorSpeed':'Adjusts the speed of the cursor when selecting locations on the map using a gamepad.','MapLocationSelectionCursorSpeedMouse':'Adjusts the speed of the cursor when selecting locations on the map using a mouse.','FocusedModeOpacity':'Sets the overlay opacity for the focused mode.','PreferredDisplayMode':'Sets the preferred display mode (fullscreen, borderless, etc.) for the game.','RefreshRate':'Sets the refresh rate for the game display.','Resolution':'Sets the display resolution for the game.','WindowHeight':'Sets the height of the game window when in windowed mode.','WindowMaximized':'When enabled, the game window will start maximized.','VSync':"Synchronizes the game's frame rate with your monitor's refresh rate to prevent screen tearing.",'DisplayGamma':'Sets the color space for monitor output. Affects how colors are displayed.','BulletImpacts':'Toggles the visibility of bullet impact effects.','ModelQuality':'Adjusts the quality of 3D models in the game. Higher quality may impact performance.','WindowWidth':'Sets the width of the game window when in windowed mode.','WindowX':'Sets the X-coordinate of the game window when in windowed mode.','WindowY':'Sets the Y-coordinate of the game window when in windowed mode.','AATechniquePreferred':'Sets the preferred anti-aliasing technique to reduce jagged edges.','AMDSuperResolution':'Enables AMD FidelityFX Super Resolution for improved performance or image quality.','AbsoluteTargetResolution':'Sets a fixed target resolution for the game.','ClutterMaxDist':'Sets the maximum distance at which clutter models are rendered.','CorpsesCullingThreshold':'Sets the threshold for culling (removing) corpses from the scene to improve performance.','DefaultSMAATechnique':'Sets the default Subpixel Morphological Antialiasing technique.','DynamicSceneResolution':'Enables dynamic adjustment of scene resolution to maintain performance.','DynamicSceneResolutionTarget':'Sets the target frame time (in milliseconds) for dynamic scene resolution adjustments.','SunShadowCascade':'Sets the quality of distant sun shadows. Higher quality uses more shadow cascades but impacts performance.','FilmicStrength':'Adjusts the strength of the filmic visual noise filter.','ShadowQuality':'Adjusts the overall quality of shadows in the game.','StaticSunshadowClipmapResolution':'Sets the resolution for static sun shadow clipmaps. Higher resolutions improve shadow quality but impact performance.','XeSSQuality':'Adjusts the quality setting for Intel XeSS (Xe Super Sampling) upscaling technology.','AMDSuperResolutionQuality':'Sets the quality level for AMD FidelityFX Super Resolution upscaling.','GTAOQuality':'Sets the quality level for Ground Truth Ambient Occlusion.','AMDContrastAdaptiveSharpeningStrength':"Adjusts the strength of AMD's Contrast Adaptive Sharpening (CAS) filter.",'ModelLodDistanceQuality':'Adjusts the distance at which model Level of Detail (LOD) changes occur.','AMDSuperResolution2Quality':'Sets the quality level for AMD FidelityFX Super Resolution 2 and 3 upscaling.','ModelLodQuality':'Sets the quality of model Level of Detail (LOD).','NVIDIAImageScaling':'Enables NVIDIA Image Scaling for improved performance and image quality on supported GPUs.','NVIDIAImageScalingQuality':'Adjusts the quality setting for NVIDIA Image Scaling.','NVIDIAImageScalingSharpness':'Sets the sharpness level for NVIDIA Image Scaling.','VRS':'Enables Variable Rate Shading to improve performance by reducing shading rate in less noticeable areas.','ParticleLighting':'Adjusts the quality of lighting effects on particles.','ParticuleResolution':'Sets the resolution of particle effects.','PersistentDamageLayer':'Enables a persistent layer for damage effects, potentially improving performance in scenes with lots of destruction.','STLodSkip':'Sets the number of Shadow Tree Levels of Detail to skip, potentially improving performance at the cost of shadow quality.','WaterCausticsMode':'Adjusts the quality of water caustics effects. Higher quality may impact performance.','WaterWaveWetness':'Enables persistent wetness effects on static geometry from water waves.','PixelPerLightmapTexel':'Adjusts the quality of lightmap textures.','ReflectionProbeHalfResolution':'Enables half-resolution reflection probes to improve performance at the cost of reflection quality.','ReflectionProbeRelighting':'Adjusts the number of stages for reflection probe relighting. More stages improve quality but impact performance.','SMAAQuality':'Sets the quality level for Subpixel Morphological Antialiasing.','SSRMode':'Sets the mode for Screen Space Reflections. Higher quality modes may impact performance.','ScreenSpaceShadowQuality':'Adjusts the quality of screen space shadows. Higher quality may impact performance.','ShadowMapResolution':'Sets the resolution of shadow maps. Higher resolutions improve shadow quality but impact performance.','SpotShadowCacheSize':'Adjusts the size of the spot shadow cache.','SpotShadowQualityLevel':'Sets the quality level for spot shadows.','SubdivisionLevel':'Adjusts the level of Catmull-Clark subdivision for smoother surfaces. Higher levels may impact performance.','UiQuality':'Sets the quality of the user interface elements.','VirtualTexturingMemoryMode':'Sets the memory mode for virtual texturing. Larger modes provide better texture quality but require more VRAM.','WeatherGridVolumesQuality':'Adjusts the quality of volumetric weather effects. Higher quality may impact performance.','DxrMode':'Enables DirectX Raytracing for improved lighting, shadows, and reflections on supported hardware.','EnableVelocityBasedBlur':'Enables radial motion blur based on player velocity for a more dynamic visual effect.','SustainabilityPauseRendering':'Pauses rendering in multiplayer when in the pause menu or out of focus to save power.','WorldStreamingQuality':'Adjusts the quality of world streaming. Higher quality may require more system resources.','SustainabilityMenuSceneResolution':'Reduces the dynamic scene resolution in non-interactive scenes to save power.','SkipIntro':'Skips the introduction movie that plays when the game is started.','ViewedSplashScreen':'Allows the player to skip the splash screen if it has been viewed at least once.','UseOSCursors':'Uses the operating system cursors instead of the custom game cursor for accessibility reasons.','ShowFPSCounter':'Displays an on-screen FPS (Frames Per Second) counter.','SkipSeasonVideo':'Controls whether the season video is shown when the player logs in for the second time after seeing it once.','SkipSeasonIntroVideo':'Controls whether the season intro video plays at all.','WeaponCycleDelay':'Sets the minimum delay (in milliseconds) between valid mouse wheel inputs for weapon cycling.','MouseUsesRawInput':'Enables raw input for the mouse, potentially improving responsiveness and accuracy.','YawSpeed':'Sets the maximum yaw (horizontal rotation) speed in degrees for gamepad and keyboard.','PitchSpeed':'Sets the maximum pitch (vertical rotation) speed in degrees for gamepad.','VehicleMouseSteerSensitivity':'Adjusts the sensitivity of mouse steering for vehicles.','GamepadMenuScrollDelayFirst':'Sets the initial delay (in milliseconds) for menu scrolling with a gamepad.','GamepadMenuScrollDelayRestStart':'Sets the starting delay (in milliseconds) for subsequent menu scrolls with a gamepad.','GamepadMenuScrollDelayRestEnd':'Sets the ending delay (in milliseconds) for subsequent menu scrolls with a gamepad.','GamepadMenuScrollDelayRestAccel':'Sets the acceleration (in milliseconds per repeat) for menu scrolling with a gamepad.','TextChatBackgroundOpacity':'Adjusts the opacity of the background for text chat.','AltShellShock':'Enables or disables muted tinnitus sound for shell shock effect.','AudioWheelActive':'Enables or disables the Audio Wheel feature.','LicensedContentVolume':'Adjusts the volume of licensed content in the game.','MonoSoundAmount':'Sets the percentage of mono sound when Mono Sound is enabled.','VoiceChatVolume':"Adjusts the volume of other players' voices in voice chat.",'SprintAssistDelayGamepad':'Sets the time (in milliseconds) at max stick deflection before sprinting is activated for gamepad.','HUDHorizBound':'Adjusts the maximum horizontal bound of the Heads-Up Display.','HUDVertBound':'Adjusts the maximum vertical bound of the Heads-Up Display.','SprintAssistDelayKBM':'Sets the time (in milliseconds) required for moving before sprinting is auto-activated for keyboard and mouse.','ADS2xZoomSensitivity':'Multiplies mouse sensitivity when aiming down sights with 2x zoom scopes.','ADS4xZoomSensitivity':'Multiplies mouse sensitivity when aiming down sights with 4x zoom scopes.','ADS6xZoomSensitivity':'Multiplies mouse sensitivity when aiming down sights with 6x zoom scopes.','ADS8xZoomSensitivity':'Multiplies mouse sensitivity when aiming down sights with 8x zoom scopes.','ADSHighZoomSensitivity':'Multiplies mouse sensitivity when aiming down sights with high zoom scopes.','ADSLowZoomSensitivity':'Multiplies mouse sensitivity when aiming down sights with low zoom scopes.','ADSTimingSensitivity':'Adjusts the timing for ADS sensitivity multipliers to take effect when aiming down sight.','MouseAirSensitivityMultiplier':'Multiplies mouse sensitivity when piloting air vehicles.','EnableGamepad':'Restricts the input device used for aiming. False for Mouse, True for Gamepad Stick.','ADSHoldBreathSensitivity':'Multiplies mouse sensitivity when holding breath while aiming down sights.','MouseFlyingVehicleInvertPitch':'Inverts vertical aim with a mouse while in an air vehicle.','MouseGroundVehicleInvertPitch':'Inverts vertical aim with a mouse while in a land vehicle.','MouseLandSensitivityMultiplier':'Multiplies mouse sensitivity when driving land vehicles.','MouseInGameTabletSensitivity':'Multiplies mouse sensitivity when selecting a target on a map through a streak.','MouseMonitorDistanceCoeff':'Adjusts the coefficient for monitor distance ADS mouse sensitivity scaling.','TacticalAdsMouseSensitivityMultiplier':'Multiplies mouse sensitivity when using tactical ADS.','MouseFlightHorizontalSensibility':'Adjusts mouse sensitivity while in an air vehicle for both axes.','MouseFlightVerticalSensibility':'Multiplies mouse sensitivity while in an air vehicle on the vertical axis only.','HTTPStreamLimitMBytes':'Sets the stream limit in megabytes.','HTTPStreamUsageLimit':'Enables or disables the stream usage limit.','ADSTimingSensitivityTouch':'Adjusts the timing for ADS sensitivity multipliers to take effect when aiming down sight for touch controls.'}