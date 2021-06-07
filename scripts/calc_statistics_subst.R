# Title     : calculate per-character statistics
# Created by: Valerii Zuev
# Created on: 6/7/2021

library(dplyr)

heatmap_filtered <- function(subs_mtx = ?data.frame, filter = ? str, file_suffix = ? str) {
  filter_list <- strsplit(filter, "")[[1]]
  jpeg(paste0("data/11_alns_stats/subs_heatmap_symmetrify", symmetrify, file_suffix, ".jpeg"),
       width = 2000, height = 2000, res = 300)
  subs_mtx %>%
    select(filter_list) %>%
    filter(row.names(subs_mtx) %in% filter_list) %>%
    filter(rowSums(across(where(is.numeric))) > 0) %>%
    as.matrix %>%
    heatmap
  dev.off()
} -> None

for (symmetrify in c("True", "False")) {
  subs_mtx <- read.csv(paste0("data/11_alns_stats/subst_mtx_symmetrify", symmetrify, ".csv"), header = T, row.names = 1)
  trans <- ("⠖$&⠄⠣⠜⠂⠤⠲⠌:⠆⠢⠿⠼⠠⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵⠦⠴■▲◂" %>% strsplit(""))[[1]]
  rownames(subs_mtx) <- trans
  colnames(subs_mtx) <- trans

  alphabet <- "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵"
  special_symbols <- "⠖⠄⠣⠜⠂⠤⠲⠌:⠆⠢⠿⠼"
  heatmap_filtered(subs_mtx = subs_mtx, filter = alphabet, file_suffix = "alphabet")
  heatmap_filtered(subs_mtx = subs_mtx, filter = special_symbols, file_suffix = "special")
}

