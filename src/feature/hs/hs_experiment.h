#ifndef TOR_HS_EXPERIMENT_H
#define TOR_HS_EXPERIMENT_H

/* Enable our experiment code paths */
#define RUN_IP_INTERSECTION_EXPERIMENT 1

/* Constants for forced intro/middle selection (40-hex RSA identity) */
#define FORCED_INTRO_FP_HEX "AA2E247DE86D7A184989A0C9E583962A8004001B"
#define FORCED_INTRO_NICK   "salokinvanguard"
#define FORCED_MID_FP_HEX   "93999A28D8CBDACDDA46A165BF0EA62FF385462C"
#define FORCED_MID_NICK     "salokinmiddle1"

#define FORCED_VANGUARD_FP_HEX   "617070AB304E5A45578141A44FF26E8D50B06629"
#define FORCED_VANGUARD_NICK     "salokinmiddle0"

#define FORCED_ENTRY_FP_HEX   "5583258D94C0DE71A8183D7EB5EE6DC950EA88F8"
#define FORCED_ENTRY_NICK     "salokinentry"
/* One-shot flag: forces first middle of the next intro circuit */
extern int g_hs_force_layer2_for_next_intro;
#define ENABLE_RELAY_COUNTRY_EXPORT
#endif /* TOR_HS_EXPERIMENT_H */


