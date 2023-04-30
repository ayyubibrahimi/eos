# Working with local (NOLA) group eye on surveillance, Ayyub has been analyzing some public records data on requests for surveillance data from the NOPD to the Real Time Crime Center (RTCC). This notebook joins police report data to the surveillance requests to try in order to answer a question about bias in surveillance requests: in an investigation for a given criminal charge, is a Black suspect more likely to be the subject of a surveillance request than a non-Black suspect? Interesting question! Originally AI answered this question with a Chi-Squared test, but I find the named statistical tests very confusing and suggested a poisson regression. I continued to be kind of curious though. There are a lot of charges, it would be interesting to model all of them. So I cloned the repo and tried fitting my own model. We start the same as AI, reading in the data and joining the two tables. I’m sort of mindlessly dropping records with missing data here for the sake of a quick example, and I’m also assuming that the two datasets refer to the same time period:

library(tidyverse)
library(brms)
library(tidybayes)

pr <- read_csv("../data/police_reports/electronic_police_report_2018_2022.csv",
               guess_max = 20000) %>%
    mutate(race_black = offender_race == "BLACK")

rtcc <- read_csv("../data/real_time_crime_center/rtcc.csv",
                 guess_max = 20000) %>%
    distinct(item_number) %>%
    mutate(rtcc_requested = 1)

rc <- pr %>%
    filter(!is.na(offender_race),
           !is.na(charge_description)) %>%
    select(item_number, race_black, charge_description) %>%
    left_join(rtcc, by = "item_number") %>%
    replace_na(list(rtcc_requested = 0)) %>%
    group_by(race_black, charge_description) %>%
    summarise(n = n(), rtcc = sum(rtcc_requested), .groups = "drop")

# From there I modeled the counts of RTCC requests as a binomial distribution, with the binomial probability depending on race and charge description (using a varying intercept for the latter):

spec <- bf(rtcc | trials(n) ~ race_black + (1 | charge_description),
           family = "binomial", center = TRUE)

model <- brm(spec,
             prior = set_prior("normal(0, 5)", class = "b"),
             data = rc, chains = 4, iter = 5000)

# The normal(0,5) prior is for the coefficient on the race_BLACK indicator, given centered data this is a wide, not very informative prior. We stick with the default student_t(3, 0, .25) prior for the standard deviation of the varying intercept distribution.
# I was thinking of useful ways to check this model. We could e.g. fit the model using all but one of the charges and then compare the posterior distribution of counts for an unseen charge with the actual counts from the held-out charge, and repeat this for each of the charges.
# And what does the model tell us? In the summary of the resulting model, we see as we might have predicted that a lot of variation is explained by the charge, and that even accounting for that, there is a positive coefficient for when race_BLACK is 1:

# Group-Level Effects: 
# ~charge_description (Number of levels: 620) 
#              Estimate Est.Error l-95% CI u-95% CI Rhat Bulk_ESS Tail_ESS
# sd(Intercept)     1.61      0.08     1.46     1.79 1.00      876     1512

# Population-Level Effects: 
#               Estimate Est.Error l-95% CI u-95% CI Rhat Bulk_ESS Tail_ESS
# Intercept         -3.58      0.10    -3.79    -3.39 1.01      567      989
# race_blackTRUE     0.34      0.03     0.29     0.40 1.00    13138     7181

#Out of curiosity, I wanted to know the most and least likely charges to result in a surveillance request, so I sampled from the appropriate coefficients in the model:

coef_summaries <- spread_draws(model, r_charge_description[charge,b]) %>%
    group_by(charge) %>%
    summarise(q05 = quantile(r_charge_description, .05),
              median = median(r_charge_description),
              q95 = quantile(r_charge_description, .95))

#First we look at the charges that were most likely to trigger surveillance footage requests. “Littering from motor vehicle” is an interesting appearance in this top 10:
#> arrange(coef_summaries, desc(median))
# A tibble: 619 × 4
 #  charge                                        q05 median   q95
  # <chr>                                       <dbl>  <dbl> <dbl>
 #1 PRINCIPAL.TO.2ND.DEGREE.MURDER               3.28   4.34  5.58
 #2 FIRST.DEGREE.MURDER                          3.61   3.92  4.24
 #3 RELATIVE.TO.PRINCIPAL.TO.ATTEMPTED.HOMICIDE  2.89   3.81  4.80
 #4 ILLEGAL.DUMPING                              3.32   3.72  4.13
 #5 SECOND.DEGREE.MURDER                         3.32   3.57  3.82
 #6 ACCESSORY.-.AGG..BATTERY                     2.66   3.50  4.35
 #7 RELATIVE.TO.INSURANCE.FRAUD                  1.84   3.48  5.21
 #8 ASSAULT.BY.DRIVE.BY.SHOOTING                 2.99   3.38  3.78
 #9 LITTERING.FROM.MOTOR.VEHICLE                 2.33   3.37  4.43
1#0 ATTEMPT.-.SECOND.DEGREEMURDER                2.82   3.09  3.36
# ℹ 609 more rows
#At the other end, charges that don’t often lead to surveillance requests:
#> arrange(coef_summaries, median)
# A tibble: 619 × 4
#   charge                                                    q05 median    q95
#   <chr>                                                   <dbl>  <dbl>  <dbl>
# 1 CDC.WARRANT#                                            -4.65  -3.44 -2.51 
# 2 WARRANT.ISSUED.BY                                       -3.97  -3.37 -2.86 
# 3 OUT.OF.STATE.FUGITIVE                                   -4.84  -3.17 -2.00 
# 4 TELEPHONE.COMMUNICATIONS;.IMPROPER.LANGUAGE;.HARASSMENT -4.57  -3.02 -1.82 
# 5 VIOLATION#                                              -4.65  -3.02 -1.83 
# 6 LOOTING                                                 -4.22  -2.41 -1.13 
# 7 HARASSING.PHONE.CALLS                                   -4.10  -2.27 -0.947
# 8 STALKING                                                -4.03  -2.25 -0.898
# 9 DOMESTIC.ABUSE.BATTERY(CHILD.ENDANGERMENT).-.SIMPLE     -3.15  -2.20 -1.45 
#10 POSSESSION.OF.MARIJUANA.(1ST.OFFENSE)                   -2.64  -2.16 -1.73 

#I can look at predicted requests for surveillance footage given a new charge that we don’t have a fit parameter for, to compare the marginal differences based on the race of the suspect:

tibble(race_black = c(T, F), charge_description = "XXXX", n = 1000) %>%
    add_predicted_draws(model, allow_new_levels = TRUE, ndraws = 200) %>%
    summarise(q_05 = quantile(.prediction, .05),
              median = median(.prediction),
              q95 = quantile(.prediction, .95),
              .groups = "drop") %>%
    select(race_black, q_05, median, q95)

#Which shows:
# A tibble: 2 × 4
#  race_black  q_05 median   q95
#  <lgl>      <dbl>  <dbl> <dbl>
# 1 FALSE          2   28.5  279.
# 2 TRUE           3   39.5  335.
# But I assume the charge is also influenced by the person’s race? Hmmn . . ..
