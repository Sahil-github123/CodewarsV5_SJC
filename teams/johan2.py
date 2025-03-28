#merged upgraded defensive strategy
#upgraded tank strategy
#by JSB, CT, SR
#fully working

from teams.helper_function import Troops, Utils

team_name = "BlueForce2_J2"
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
    atd=Troops.troops_data

    team_signal = f"E{int(elixir_available)}|{get_active_troops(my_troops)}"
    
    bulk_troops = {'Skeleton':False, 'Archer':False,'Minion':False, 'Barbarian':False}
    
    # ALWAYS deploy something if elixir is high - this is critical
    # if elixir_available >= 9 and deployable_troops:
    #     for cheap_troop in [Troops.skeleton, Troops.archer, Troops.knight]:
    #         if cheap_troop in deployable_troops:
    #             deploy_list.list_.append((cheap_troop, (0, 0)))
    #             return
    #     # If no cheap troops, deploy whatever we have
    #     deploy_list.list_.append((deployable_troops[0], (0, 0)))
    #     return

    # 1. DEFENSIVE COUNTER - High priority
    if opp_troops and elixir_available >= 3 and deployable_troops:
        for enemy in opp_troops:
            countered=defensive_action(enemy, deployable_troops, elixir_available,bulk_troops,atd)
            if not countered:
                unspecific_counter(enemy, deployable_troops, elixir_available, atd)
                
    # 2. OFFENSIVE STRATEGY - Giant or Prince pushes
    if elixir_available >= 5 and deployable_troops:
        # Try primary attack strategies
        if handle_offense(my_troops, deployable_troops, elixir_available):
            return
    
    # 3. GUARANTEED DEPLOYMENT - Always deploy something if we have elixir
    if elixir_available >= 3 and deployable_troops:
        for troop in deployable_troops:
            if troop not in [Troops.giant, Troops.valkyrie, Troops.dragon, Troops.skeleton]:
                deploy_list.list_.append((troop, (0, 0)))
                break

def defensive_action(enemy, deployable_troops, elixir_available,bulk_troops,atd):
    pos = enemy.position
    splash_troops = [Troops.wizard, Troops.dragon, Troops.valkyrie]

    if enemy.name in bulk_troops and (not bulk_troops[enemy.name]) and (enemy.target==None or enemy.target=='Tower 1' or enemy.target=='Tower 2') :
            if 0 <= pos[1] <= 50:
                splash_scores = {'Wizard': 3, 'Dragon': 4, 'Valkyrie': 2}
                if enemy.type == 'air':
                    splash_scores['Valkyrie'] = 0  # Valkyrie cannot counter air troops
                elif enemy.type == 'ground':
                    splash_scores['Valkyrie'] = 5

                # Sort splash troops by score, deploy the highest scoring troop available with sufficient elixir
                splash_troops.sort(key=lambda x: splash_scores[x], reverse=True)
                for troop in splash_troops:
                    if troop in deployable_troops and elixir_available >= atd[troop].elixir and splash_scores[troop] > 0:
                        # print(atd[troop].attack_range)
                        deploy_list.list_.append((troop, (pos[0],max(0, pos[1] - atd[troop].attack_range*2))))
                        # deploy_list.list_.append((troop, (25, 50)))
                        bulk_troops[enemy.name] = True  # Mark this bulk troop as countered
                        #print(bulk_troops)
                        return True
    
    tank_troops = ['Giant', 'Knight', 'Prince','Balloon']
    if enemy.name in tank_troops :
        if 0 <= pos[1] <= 50:
            tankbuster_scores={'Skeleton':5,'Minion': 4,'Wizard':3, 'Archer': 2}
            if enemy.type == 'air':
                tankbuster_scores['Skeleton'] = 0

            # Sort tankbuster troops by score, deploy the highest scoring troop available with sufficient elixir
            for troop, score in sorted(tankbuster_scores.items(), key=lambda item: item[1], reverse=True):
                if troop in deployable_troops and elixir_available >= atd[troop].elixir and score>0:
                    deploy_list.list_.append((troop, (pos[0], max(0, pos[1] - atd[troop].attack_range))))
                    return True
                
    if enemy.name=='Wizard':
        if 0 <= pos[1] <= 50:
            if Troops.prince in deployable_troops and elixir_available >= atd['Prince'].elixir:
                deploy_list.list_.append((Troops.prince, (pos[0], max(0, pos[1] - atd['Prince'].attack_range))))
                return True
    
    if enemy.name=='Valkyrie':
        if 0 <= pos[1] <= 50:
            air_troops_scores = {'Minion': 1, 'Dragon': 3}
            for troop, score in sorted(air_troops_scores.items(), key=lambda item: item[1], reverse=True):
                if troop in deployable_troops and elixir_available >= atd[troop].elixir:
                    deploy_list.list_.append((troop, (pos[0], max(0, pos[1] - atd[troop].attack_range))))
                    return True
        
    if enemy.name == 'Dragon':
        # Match with dragon, minion, wizard, archer in that order
        if 0 <= pos[1] <= 50:
            dragon_scores = {'Dragon': 4, 'Minion': 3, 'Wizard': 2, 'Archer': 1}
            for troop, score in sorted(dragon_scores.items(), key=lambda item: item[1], reverse=True):
                if troop in deployable_troops and elixir_available >= atd[troop].elixir:
                    deploy_list.list_.append((troop, (pos[0], max(0, pos[1] - atd[troop].attack_range))))
                    return True
    # If no specific counter, deploy any available troop that can attack the enemy (NOT Giant/balloon)

        
def unspecific_counter(enemy, deployable_troops, elixir_available, atd):
    pos = enemy.position
    for troop in deployable_troops:
        #print("####")

        if 0 <= pos[1] <= 50:
            #print(enemy)
            #print(enemy.name)
            #print(enemy.position)   
            if troop not in ['Giant','Balloon']:
                if elixir_available >= atd[troop].elixir and enemy.target==None or enemy.target=='Tower 1' or enemy.target=='Tower 2':
                    if enemy.type == 'air' and atd[troop].type in ['air', 'both']:
                        deploy_list.list_.append((troop, (pos[0], max(0, pos[1] - atd[troop].attack_range))))
                        return
                    elif enemy.type == 'ground' and atd[troop].type in ['ground', 'both']:
                        deploy_list.list_.append((troop, (pos[0], max(0, pos[1] - atd[troop].attack_range))))
                        return


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