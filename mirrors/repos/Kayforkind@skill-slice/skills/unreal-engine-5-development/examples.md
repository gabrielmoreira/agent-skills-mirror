# UE5 Examples — Complete, Compiling Reference Code

Companion to [SKILL.md](SKILL.md). Module name is `MyGame` throughout; rename `MYGAME_API`/includes to match your module. Targets UE 5.3–5.5.

## Build.cs

`Source/MyGame/MyGame.Build.cs`:

```csharp
using UnrealBuildTool;

public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        // Types used in Public/ headers → Public deps
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core", "CoreUObject", "Engine", "InputCore",
            "EnhancedInput",                                   // Enhanced Input
            "GameplayAbilities", "GameplayTags", "GameplayTasks" // GAS trio
        });

        // Used only in Private/ .cpp files → Private deps
        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "UMG", "Slate", "SlateCore"                        // if doing UI
        });
    }
}
```

`Source/MyGame.Target.cs` (game) — the editor Target.cs is identical with `Type = TargetType.Editor`:

```csharp
using UnrealBuildTool;
using System.Collections.Generic;

public class MyGameTarget : TargetRules
{
    public MyGameTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_4;
        ExtraModuleNames.Add("MyGame");
    }
}
```

Primary module boilerplate, `Private/MyGame.cpp`:

```cpp
#include "Modules/ModuleManager.h"
IMPLEMENT_PRIMARY_GAME_MODULE(FDefaultGameModuleImpl, MyGame, "MyGame");
```

## Gameplay framework stack

GameMode (server-only rules; note: pawn/controller classes are assigned in the BP child or Config, never hardcoded paths):

```cpp
// Public/Core/MyGameMode.h
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class MYGAME_API AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    virtual void PostLogin(APlayerController* NewPlayer) override;

protected:
    UPROPERTY(EditDefaultsOnly, Category="Rules", meta=(ClampMin="1"))
    int32 ScoreToWin = 10;

    UFUNCTION(BlueprintCallable, Category="Rules")
    void ReportKill(APlayerState* Killer);
};
```

GameState — shared, replicated match data:

```cpp
// Public/Core/MyGameState.h
#pragma once
#include "GameFramework/GameStateBase.h"
#include "MyGameState.generated.h"

UENUM(BlueprintType)
enum class EMatchPhase : uint8 { Warmup, Playing, PostMatch };

UCLASS()
class MYGAME_API AMyGameState : public AGameStateBase
{
    GENERATED_BODY()
public:
    UPROPERTY(ReplicatedUsing=OnRep_Phase, BlueprintReadOnly, Category="Match")
    EMatchPhase Phase = EMatchPhase::Warmup;

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

protected:
    UFUNCTION()
    void OnRep_Phase();   // clients react here (UI, music) — server sets Phase directly
};
```

```cpp
// Private/Core/MyGameState.cpp
#include "Core/MyGameState.h"
#include "Net/UnrealNetwork.h"

void AMyGameState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyGameState, Phase);
}

void AMyGameState::OnRep_Phase()
{
    // broadcast a BlueprintAssignable delegate for UI here
}
```

## Character (Enhanced Input)

Header — asset slots are UPROPERTYs assigned in the BP child (`BP_Hero`), never `FObjectFinder` paths:

```cpp
// Public/Characters/HeroCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "HeroCharacter.generated.h"

class UInputMappingContext;
class UInputAction;

UCLASS()
class MYGAME_API AHeroCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AHeroCharacter();

protected:
    virtual void NotifyControllerChanged() override;                 // add IMC here (server travel & possession-safe)
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    // --- Input assets (assigned in BP child) ---
    UPROPERTY(EditDefaultsOnly, Category="Input")
    TObjectPtr<UInputMappingContext> DefaultMappingContext;

    UPROPERTY(EditDefaultsOnly, Category="Input")
    TObjectPtr<UInputAction> MoveAction;      // Value: Axis2D (WASD swizzled in the IMC)

    UPROPERTY(EditDefaultsOnly, Category="Input")
    TObjectPtr<UInputAction> LookAction;      // Value: Axis2D

    UPROPERTY(EditDefaultsOnly, Category="Input")
    TObjectPtr<UInputAction> JumpAction;      // Value: Digital(bool)

    // --- Handlers ---
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
};
```

```cpp
// Private/Characters/HeroCharacter.cpp
#include "Characters/HeroCharacter.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/PlayerController.h"

AHeroCharacter::AHeroCharacter()
{
    PrimaryActorTick.bCanEverTick = false;    // opt in only when needed
}

void AHeroCharacter::NotifyControllerChanged()
{
    Super::NotifyControllerChanged();

    if (const APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            Subsystem->ClearAllMappings();
            if (DefaultMappingContext)
            {
                Subsystem->AddMappingContext(DefaultMappingContext, /*Priority*/ 0);
            }
        }
    }
}

void AHeroCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // CastChecked: if the project isn't configured for EnhancedInput, fail loudly at startup
    UEnhancedInputComponent* EIC = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);

    if (MoveAction) EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AHeroCharacter::Move);
    if (LookAction) EIC->BindAction(LookAction, ETriggerEvent::Triggered, this, &AHeroCharacter::Look);
    if (JumpAction)
    {
        EIC->BindAction(JumpAction, ETriggerEvent::Started,   this, &ACharacter::Jump);
        EIC->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
    }
}

void AHeroCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();
    if (Controller && !Axis.IsNearlyZero())
    {
        const FRotator YawRot(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(YawRot).GetUnitAxis(EAxis::X), Axis.Y);  // forward
        AddMovementInput(FRotationMatrix(YawRot).GetUnitAxis(EAxis::Y), Axis.X);  // right
    }
}

void AHeroCharacter::Look(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();
    AddControllerYawInput(Axis.X);
    AddControllerPitchInput(Axis.Y);
}
```

Editor-side setup: create `IA_Move` (Axis2D), `IA_Look` (Axis2D), `IA_Jump` (Digital); in `IMC_Default` map WASD to IA_Move with **Swizzle Input Axis Values** + **Negate** modifiers to fold four keys into one 2D axis, mouse XY to IA_Look, Space to IA_Jump; assign all four assets on `BP_Hero`.

## GAS starter

Minimal correct wiring: ASC lives on **PlayerState** (survives respawn), Character implements `IAbilitySystemInterface`, init happens on **both** server (`PossessedBy`) and client (`OnRep_PlayerState`). Requires the `GameplayAbilities` plugin enabled in .uproject and the three GAS modules in Build.cs (above).

```cpp
// Public/Core/MyPlayerState.h
#pragma once
#include "GameFramework/PlayerState.h"
#include "AbilitySystemInterface.h"
#include "MyPlayerState.generated.h"

class UAbilitySystemComponent;
class UMyAttributeSet;

UCLASS()
class MYGAME_API AMyPlayerState : public APlayerState, public IAbilitySystemInterface
{
    GENERATED_BODY()
public:
    AMyPlayerState();
    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override { return ASC; }
    UMyAttributeSet* GetAttributes() const { return Attributes; }

protected:
    UPROPERTY(VisibleAnywhere, Category="GAS")
    TObjectPtr<UAbilitySystemComponent> ASC;

    UPROPERTY()
    TObjectPtr<UMyAttributeSet> Attributes;
};
```

```cpp
// Private/Core/MyPlayerState.cpp
#include "Core/MyPlayerState.h"
#include "AbilitySystemComponent.h"
#include "Abilities/MyAttributeSet.h"

AMyPlayerState::AMyPlayerState()
{
    ASC = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("ASC"));
    ASC->SetIsReplicated(true);
    // Mixed: GameplayEffects replicate to owner only; tags/cues to everyone. Right default for player-owned ASCs.
    ASC->SetReplicationMode(EGameplayEffectReplicationMode::Mixed);

    Attributes = CreateDefaultSubobject<UMyAttributeSet>(TEXT("Attributes"));

    SetNetUpdateFrequency(60.f);   // PlayerState default is very low; too slow for ability state
}
```

Attribute set:

```cpp
// Public/Abilities/MyAttributeSet.h
#pragma once
#include "AttributeSet.h"
#include "AbilitySystemComponent.h"
#include "MyAttributeSet.generated.h"

#define ATTRIBUTE_ACCESSORS(ClassName, PropertyName) \
    GAMEPLAYATTRIBUTE_PROPERTY_GETTER(ClassName, PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_GETTER(PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_SETTER(PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_INITTER(PropertyName)

UCLASS()
class MYGAME_API UMyAttributeSet : public UAttributeSet
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_Health, Category="Attributes")
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_MaxHealth, Category="Attributes")
    FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, MaxHealth)

    virtual void PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

protected:
    UFUNCTION() void OnRep_Health(const FGameplayAttributeData& OldValue);
    UFUNCTION() void OnRep_MaxHealth(const FGameplayAttributeData& OldValue);
};
```

```cpp
// Private/Abilities/MyAttributeSet.cpp
#include "Abilities/MyAttributeSet.h"
#include "GameplayEffectExtension.h"
#include "Net/UnrealNetwork.h"

void UMyAttributeSet::PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data)
{
    Super::PostGameplayEffectExecute(Data);
    if (Data.EvaluatedData.Attribute == GetHealthAttribute())
    {
        SetHealth(FMath::Clamp(GetHealth(), 0.f, GetMaxHealth()));  // clamp AFTER effects apply
    }
}

void UMyAttributeSet::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME_CONDITION_NOTIFY(UMyAttributeSet, Health,    COND_None, REPNOTIFY_Always);
    DOREPLIFETIME_CONDITION_NOTIFY(UMyAttributeSet, MaxHealth, COND_None, REPNOTIFY_Always);
}

void UMyAttributeSet::OnRep_Health(const FGameplayAttributeData& OldValue)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, Health, OldValue);
}
void UMyAttributeSet::OnRep_MaxHealth(const FGameplayAttributeData& OldValue)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, MaxHealth, OldValue);
}
```

Character-side init — the part everyone gets wrong (must run on server **and** client):

```cpp
// In AHeroCharacter (add IAbilitySystemInterface to the class as well)

void AHeroCharacter::PossessedBy(AController* NewController)   // SERVER
{
    Super::PossessedBy(NewController);
    if (AMyPlayerState* PS = GetPlayerState<AMyPlayerState>())
    {
        PS->GetAbilitySystemComponent()->InitAbilityActorInfo(PS, this);
        // server-only: grant startup abilities / apply default GE_InitStats here
    }
}

void AHeroCharacter::OnRep_PlayerState()                        // CLIENT
{
    Super::OnRep_PlayerState();
    if (AMyPlayerState* PS = GetPlayerState<AMyPlayerState>())
    {
        PS->GetAbilitySystemComponent()->InitAbilityActorInfo(PS, this);
    }
}
```

From here: author `GE_Damage` / `GE_InitStats` GameplayEffect BPs (data, not code), grant `UGameplayAbility` subclasses on the server with `ASC->GiveAbility(FGameplayAbilitySpec(AbilityClass, 1, InputID))`, and drive every stat change through `ApplyGameplayEffectToSelf/Target` — never `SetHealth` directly from gameplay code.

## Packaging scripts

`Tools/package_win64.bat`:

```bat
@echo off
setlocal
set UE_ROOT=C:\Program Files\Epic Games\UE_5.4
set PROJECT=D:\Dev\MyGame\MyGame.uproject
set OUT=D:\Builds\MyGame

call "%UE_ROOT%\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun ^
  -project="%PROJECT%" -platform=Win64 -clientconfig=Shipping ^
  -build -cook -stage -pak -iostore -prereqs ^
  -archive -archivedirectory="%OUT%" ^
  -unattended -utf8output -nop4

if %ERRORLEVEL% neq 0 ( echo PACKAGE FAILED & exit /b 1 )
echo Packaged to %OUT%
```

PowerShell equivalent:

```powershell
$UE = 'C:\Program Files\Epic Games\UE_5.4'
& "$UE\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun `
    -project='D:\Dev\MyGame\MyGame.uproject' -platform=Win64 -clientconfig=Shipping `
    -build -cook -stage -pak -iostore -prereqs `
    -archive -archivedirectory='D:\Builds\MyGame' -unattended -utf8output -nop4
if ($LASTEXITCODE -ne 0) { throw "Package failed ($LASTEXITCODE)" }
```

## Automation test

Runs headlessly via the command in [reference.md](reference.md#agent-command-lines); shows up under `MyGame.` in the test filter.

```cpp
// Private/Tests/HealthClampTest.cpp
#include "Misc/AutomationTest.h"
#include "Abilities/MyAttributeSet.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHealthClampTest,
    "MyGame.Attributes.HealthClampsToMax",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FHealthClampTest::RunTest(const FString& Parameters)
{
    UMyAttributeSet* Set = NewObject<UMyAttributeSet>();
    Set->InitMaxHealth(100.f);
    Set->InitHealth(150.f);                 // over max on purpose

    // Simulate the clamp path (PostGameplayEffectExecute clamps in real flow)
    Set->SetHealth(FMath::Clamp(Set->GetHealth(), 0.f, Set->GetMaxHealth()));

    TestEqual(TEXT("Health clamped to MaxHealth"), Set->GetHealth(), 100.f);
    TestTrue(TEXT("Health never negative"), Set->GetHealth() >= 0.f);
    return true;
}
```

For world-dependent tests use `IMPLEMENT_COMPLEX_AUTOMATION_TEST` or the **Functional Testing** framework (`AFunctionalTest` actors placed in a `Maps/Test/` gym map, run with `Automation RunTests Project.Functional`).
