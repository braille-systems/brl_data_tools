# Title     : Validate NNets trained on different datasets
# Created by: Valerii Zuev
# Created on: 5/29/2021

library(dplyr)

here::here("data/script_stats", "nn_validate_result.csv") %>% # path relative to the Git root. Works in R Plugin for IntelliJ IDEs
  read.csv(fileEncoding = "UTF-8-BOM") %>%
  group_by(ssl) %>%
  group_by(data, .add = T) %>%
  summarise(
    mean.precision = mean(precision),
    mean.recall = mean(recall),
    mean.f1 = mean(f1),
  ) %>%
  relocate(data) %>%
  arrange(data) %>%
  xtable::xtable(digits = 3,
                 caption = "statistics (average per 3 training)",
                 label = "table:validate_results") %>%
  print(include.rownames = F)
