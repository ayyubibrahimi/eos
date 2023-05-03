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

spec <- bf(rtcc | trials(n) ~ race_black + (1 | charge_description),
           family = "binomial", center = TRUE)

model <- brm(spec,
             prior = set_prior("normal(0, 5)", class = "b"),
             data = rc, chains = 4, iter = 5000)

coef_summaries <- spread_draws(model, r_charge_description[charge,b]) %>%
    group_by(charge) %>%
    summarise(q05 = quantile(r_charge_description, .05),
              median = median(r_charge_description),
              q95 = quantile(r_charge_description, .95))


tibble(race_black = c(T, F), charge_description = "XXXX", n = 1000) %>%
    add_predicted_draws(model, allow_new_levels = TRUE, ndraws = 200) %>%
    summarise(q_05 = quantile(.prediction, .05),
              median = median(.prediction),
              q95 = quantile(.prediction, .95),
              .groups = "drop") %>%
    select(race_black, q_05, median, q95)
