#ifndef TOR_HS_EXPERIMENT_H
#define TOR_HS_EXPERIMENT_H

/* Enable our experiment code paths */
#define RUN_IP_INTERSECTION_EXPERIMENT 1

/* Constants for forced intro/middle selection (40-hex RSA identity) */
#define FORCED_INTRO_FP_HEX "5583258D94C0DE71A8183D7EB5EE6DC950EA88F8"
#define FORCED_INTRO_NICK   "salokinentry" 

#define FORCED_MID_FP_HEX   "5835631C79E55CDFDCF9E2D14CB994325AEB3162"
#define FORCED_MID_NICK     "emir"

/* One-shot flag: forces first middle of the next intro circuit */
extern int g_hs_force_layer2_for_next_intro;

#endif /* TOR_HS_EXPERIMENT_H */

