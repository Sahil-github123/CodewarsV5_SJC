from teams.helper_function import Troops, Utils

team_name = "AggroForce_X"
troops = [
    Troops.giant,
    Troops.prince,
    Troops.wizard,
    Troops.dragon,
    Troops.valkyrie,
    Troops.knight,
    Troops.minion,
    Troops.skeleton
]
deploy_list = Troops([])
team_signal = ""

def deploy(arena_data: dict):
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

    # **High Elixir Attack (>= 9)** - Deploy strong push
    if elixir_available >= 9 and deployable_troops:
        if Troops.giant in deployable_troops:
            deploy_list.list_.append((Troops.giant, (-20, 0)))
            if Troops.wizard in deployable_troops:
                deploy_list.list_.append((Troops.wizard, (-15, 0)))
            return

    # **Prince Rush Attack** - Quick offensive push
    if Troops.prince in deployable_troops and elixir_available >= 5:
        deploy_list.list_.append((Troops.prince, (20, 0)))
        return

    # **Giant Push with Support**
    if Troops.giant in deployable_troops and elixir_available >= 5:
        deploy_list.list_.append((Troops.giant, (-20, 0)))
        if Troops.minion in deployable_troops and elixir_available >= 3:
            deploy_list.list_.append((Troops.minion, (-15, 0)))
        return

    # **Always Deploy Something If Possible**
    if deployable_troops and elixir_available >= 3:
        deploy_list.list_.append((deployable_troops[0], (0, 0)))

def get_active_troops(my_troops):
    names = [t.name for t in my_troops]
    if "Giant" in names:
        return "GW+" if any(n in names for n in ["Wizard", "Valkyrie", "Dragon", "Minion"]) else "GW"
    if "Prince" in names:
        return "PW+" if any(n in names for n in ["Wizard", "Valkyrie", "Dragon", "Minion"]) else "PW"
    return "OF"  # Offensive Mode

