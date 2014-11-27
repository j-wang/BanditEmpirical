# Utility Functions
library(magrittr)

samplefile <- function(filename, fraction) {
  system(paste("zcat <", filename, "| perl -ne 'print if (rand() < ",
               fraction, ")'"), intern=TRUE)
}

# Process a line of the Webscope Data
proc_line <- function(l, filename) {
  gsub("[1-9]:", "", l) %>%
  gsub(pattern="\\|user ", replacement="", perl=TRUE) %>%
  gsub(pattern="\\|", replacement="", perl=TRUE) %>%
  write(file=filename)
}

# Generates header labels
print_header <- function() {
  feature_gen <- function(s) {
    sapply(c(2:6, 1), FUN=function(i) paste(s, i, sep=""))
  }
  
  feat_vec <- vector()
  for (i in 1:22) {
    feat_vec <- c(feat_vec, paste("a", i, "_id", sep=""))
    feat_vec <- c(feat_vec, feature_gen(paste("a", i, "_feat", sep="")))
  }
  
  c("timestamp", "article_id", "click") %>%
  c(feature_gen("user_feat"), feat_vec) %>%
  c("a24_id", "a24_feat7", "a25_id", feature_gen("a25_feat"))
}