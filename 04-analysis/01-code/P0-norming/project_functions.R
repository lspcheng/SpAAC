# 1. Basic Libraries ----

#install.packages("")

# Data Wrangling
library(MASS, exclude = "select")
library(tidyverse)
library(janitor)
library(mgsub)
library(stopwords)

# Plots
library(ggplot2)
library(viridis)
library(ghibli)
library(RColorBrewer)
if (!require("ggthemes")) {install.packages("ggthemes"); require("ggthemes")}  
options(dplyr.summarise.inform = FALSE)
library(patchwork)
if (!require(devtools)) { install.packages('devtools') }
# devtools::install_github('erocoar/gghalves')
library(gghalves)

## 1a. Visualization Libs ----

# Create tables
library(gt)
library(webshot)
library(xtable)

# Special Plots
library(ggridges)


## 1b. Analysis Libs ----

# PCA
library(FactoMineR)
library(paran)
library(GPArotation)

# Clustering
library(corrplot)
library(cluster)
library(factoextra)
library(NbClust)
library(fpc)
library(dendextend)

# Regression
library(lme4)
library(lmerTest)
library(broom)
library(broom.mixed)

# Resolve package conflicts
# select <- dplyr::select


# 2. Basic Functions ----

# general standardized ggplot theme
gg_theme <- function() {
  theme_bw() +
    theme(plot.title=element_text(size=25),
          plot.subtitle=element_text(size=15, face="italic"),
          axis.title=element_text(size=20),
          axis.text=element_text(size=15),
          strip.background =element_rect(fill="white"),
          strip.text = element_text(size=15))+
    theme(legend.title = element_text(size=15, face="bold"),
          legend.text=element_text(size=15))
}

# Standard error function
std.error <- function(x, na.rm = T) {
  sqrt(var(x, na.rm = na.rm)/length(x[complete.cases(x)]))
}

### Filter outliers beyond 3 SD
filter_outliers <- function(df, col){
  df <- df %>% 
    filter({{ col }} > (mean({{ col }}) - sd({{ col }})*3) & 
             {{ col }} < (mean({{ col }}) + sd({{ col }})*3)) 
}