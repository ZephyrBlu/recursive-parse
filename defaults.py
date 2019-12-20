standard_player_match = [
    ('\\w+ +[v,V][s,S]\\.? +\\w+', 'search'),
    ('.vs\\.?.', 'split'),
]

standard_ignore_units = [
    'AdeptPhaseShift',
    'Larva',
    'LocustMP',
    'OracleStasisTrap',
    'Interceptor',
    'MULE',
    'AutoTurret',
    'Egg',
    'TransportOverlordCocoon',
    'OverlordCocoon',
    'LurkerMPEgg',
    'LocustMPFlying',
    'LocustMPPrecursor',
    'InfestedTerransEgg',
    'InfestorTerran',
    'BroodlingEscort',
    'Broodling',
    'RavagerCocoon',
    'BanelingCocoon',
    'BroodLordCocoon',
]

standard_merge_units = {
    'ObserverSiegeMode': 'Observer',
    'WarpPrismPhasing': 'WarpPrism',
    'WidowMineBurrowed': 'WindowMine',
    'SiegeTankSieged': 'SiegeTank',
    'ThorAP': 'Thor',
    'VikingFighter': 'Viking',
    'VikingAssault': 'Viking',
    'LiberatorAG': 'Liberator',
    'OverseerSiegeMode': 'Overseer',
    'OverlordTransport': 'Overlord',
    'LurkerMP': 'Lurker',
    'LurkerMPBurrowed': 'Lurker',
    'SwarmhostMP': 'Swarmhost',
}
