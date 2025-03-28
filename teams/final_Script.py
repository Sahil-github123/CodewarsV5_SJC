from teams.helper_function import Troops, Utils

team_name = "BlueForce"
troops = [
    Troops.giant,
    Troops.prince,
    Troops.wizard, 
    Troops.dragon,
    Troops.valkyrie,
    Troops.knight,
    Troops.archer,
    Troops.skeleton
]
deploy_list = Troops([])
team_signal = ""

def deploy(arena_data: dict):
    """
    DON'T TEMPER DEPLOY FUNCTION
    """
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

def logic(arena_data: dict):
    global team_signal
    my_tower = arena_data["MyTower"]
    opp_tower = arena_data["OppTower"]
    my_troops = arena_data["MyTroops"]
    opp_troops = arena_data["OppTroops"]

    elixir_available = my_tower.total_elixir
    deployable_troops = my_tower.deployable_troops

    team_signal = f"E{int(elixir_available)}|{get_active_troops(my_troops)}"
    
    # ALWAYS deploy something if elixir is high - this is critical
    if elixir_available >= 9 and deployable_troops:
        for cheap_troop in [Troops.skeleton, Troops.archer, Troops.knight]:
            if cheap_troop in deployable_troops:
                deploy_list.list_.append((cheap_troop, (0, 0)))
                return
        # If no cheap troops, deploy whatever we have
        deploy_list.list_.append((deployable_troops[0], (0, 0)))
        return

    # 1. DEFENSIVE COUNTER - High priority
    if opp_troops and elixir_available >= 3 and deployable_troops:
        closest_enemy = min(
            opp_troops,
            key=lambda t: Utils.calculate_distance(my_tower.position, t.position, False)
        )
        
        # Try to counter enemy
        if handle_enemy_threat(closest_enemy, deployable_troops, elixir_available):
            return

    # 2. OFFENSIVE STRATEGY - Giant or Prince pushes
    if elixir_available >= 5 and deployable_troops:
        # Try primary attack strategies
        if handle_offense(my_troops, deployable_troops, elixir_available):
            return
    
    # 3. GUARANTEED DEPLOYMENT - Always deploy something if we have elixir
    if elixir_available >= 3 and deployable_troops:
        deploy_list.list_.append((deployable_troops[0], (0, 0)))

def handle_enemy_threat(enemy, deployable_troops, elixir_available):
    """Simple counter system that always deploys something against threats"""
    pos = enemy.position
    counter_deployed = False
    
    # Air threats
    if enemy.type == "air":
        if Troops.wizard in deployable_troops and elixir_available >= 5:
            deploy_list.list_.append((Troops.wizard, (pos[0] * 0.8, pos[1] * 0.8)))
            counter_deployed = True
        elif Troops.archer in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.archer, (pos[0] * 0.8, pos[1] * 0.8)))
            counter_deployed = True
    
    # Tank threats (Giant)
    elif enemy.name == "Giant":
        if Troops.skeleton in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.skeleton, (pos[0] * 0.9, pos[1] * 0.9)))
            counter_deployed = True
        elif Troops.prince in deployable_troops and elixir_available >= 5:
            deploy_list.list_.append((Troops.prince, (pos[0] * 0.9, pos[1] * 0.9)))
            counter_deployed = True
    
    # Fast threats (Prince)
    elif enemy.name == "Prince":
        if Troops.skeleton in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.skeleton, (pos[0] * 0.9, pos[1] * 0.9)))
            counter_deployed = True
        elif Troops.knight in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.knight, (pos[0] * 0.9, pos[1] * 0.9)))
            counter_deployed = True
    
    # Splash threats (Wizard, Valkyrie)
    elif enemy.name in ["Wizard", "Valkyrie"]:
        if Troops.knight in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.knight, (pos[0] * 0.9, pos[1] * 0.9)))
            counter_deployed = True
    
    return counter_deployed

def handle_offense(my_troops, deployable_troops, elixir_available):
    """Simplified offensive strategy that always deploys something"""
    # Find existing troops on field
    giants = [t for t in my_troops if t.name == "Giant"]
    princes = [t for t in my_troops if t.name == "Prince"]
    
    # Support existing Giants
    if giants:
        giant = giants[0]
        giant_pos = giant.position
        
        # Deploy support behind Giant based on what's available
        if Troops.wizard in deployable_troops and elixir_available >= 5:
            deploy_list.list_.append((Troops.wizard, (giant_pos[0] + 5, giant_pos[1])))
            return True
        elif Troops.archer in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.archer, (giant_pos[0] + 5, giant_pos[1])))
            return True
    
    # Support existing Princes
    elif princes:
        prince = princes[0]
        prince_pos = prince.position
        
        # Deploy support ahead of Prince since Prince is fast
        if Troops.knight in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.knight, (prince_pos[0] + 8, prince_pos[1])))
            return True
        elif Troops.valkyrie in deployable_troops and elixir_available >= 4:
            deploy_list.list_.append((Troops.valkyrie, (prince_pos[0] + 8, prince_pos[1])))
            return True
    
    # Start new offensive
    else:
        # Determine side based on enemy density
        left_density = sum(1 for t in my_troops if t.position[0] < 0)
        right_density = sum(1 for t in my_troops if t.position[0] > 0)
        target_side = -15 if left_density <= right_density else 15

        # Start Giant push
        if Troops.giant in deployable_troops and elixir_available >= 5:
            deploy_list.list_.append((Troops.giant, (target_side, 0)))
            return True
        # Start Prince push
        elif Troops.prince in deployable_troops and elixir_available >= 5:
            deploy_list.list_.append((Troops.prince, (target_side, 0)))
            return True
        # Start cheaper offensive
        elif Troops.knight in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.knight, (0, 0)))
            return True
    return False

def get_active_troops(my_troops):
    """String describing what types of troops are on the field."""
    names = [t.name for t in my_troops]
    if "Giant" in names:
        return "GW+" if any(n in names for n in ["Wizard", "Valkyrie", "Dragon", "Archer"]) else "GW"
    if "Prince" in names:
        return "PW+" if any(n in names for n in ["Wizard", "Valkyrie", "Dragon", "Archer"]) else "PW"
    return "DF"