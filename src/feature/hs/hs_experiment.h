#ifndef TOR_HS_EXPERIMENT_H
#define TOR_HS_EXPERIMENT_H

/* Enable our experiment code paths */
#define RUN_IP_INTERSECTION_EXPERIMENT 1

/* Constants for forced intro/middle selection (40-hex RSA identity) */
#define FORCED_INTRO_FP_HEX "hash"
#define FORCED_INTRO_NICK   "nickname"
#define FORCED_MID_FP_HEX   "hash"
#define FORCED_MID_NICK     "nickname"

#define FORCED_VANGUARD_FP_HEX   "hash"
#define FORCED_VANGUARD_NICK     "nickname"

#define FORCED_ENTRY_FP_HEX   "hash"
#define FORCED_ENTRY_NICK     "nickname"
/* One-shot flag: forces first middle of the next intro circuit */
extern int g_hs_force_layer2_for_next_intro;
#define ENABLE_RELAY_COUNTRY_EXPORT
#endif /* TOR_HS_EXPERIMENT_H */


