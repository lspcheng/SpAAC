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
library(emmeans)

# Resolve package conflicts
# select <- dplyr::select


# 2. Basic Functions ----
options(scipen=999)

# basic descriptive stats sumarization
quick_summarize <- function(df, col, na.rm=FALSE){
  col = enquo(col)
  df %>%  summarize(across(!!col, list(median= ~ median(.x, na.rm=na.rm), mean= ~ mean(.x, na.rm=na.rm),
                                       sd= ~ sd(.x, na.rm=na.rm), min= ~ min(.x, na.rm=na.rm), 
                                       max= ~ max(.x, na.rm=na.rm))))
}

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

# 3. Plot Functions ----
# Basic stat_summary mean plot
summary_mean_plot <- function(df, x, y, group=NULL, fill_alpha=0.2, color=FALSE, viridis=FALSE, full_scale=FALSE, scale_steps=1, angle_axis_labels=FALSE) {
  x = enquo(x)
  y = enquo(y)
  group = enquo(group)
  min_y <- min(df %>% pull(!!y))
  max_y <- max(df %>% pull(!!y))
  
  if(color == TRUE){
    plot <-
      df %>% 
      ggplot(aes(x=(!!x), y=(!!y), color=(!!group), fill=(!!group), group=(!!group)))
  } else {
    plot <-
      df %>% 
      ggplot(aes(x=(!!x), y=(!!y), color=NULL, fill=(!!group), group=(!!group)))
  }
  plot <- plot +
    stat_summary(fun="mean", geom="col", position=position_dodge(0.95), alpha=fill_alpha)  +
    stat_summary(fun.data="mean_se", geom="pointrange", position=position_dodge(0.95)) +
    stat_summary(fun.data="mean_se", geom="errorbar", position=position_dodge(0.95), width=0.1) +
    gg_theme()
  
  if(viridis == TRUE){
    plot <- plot +
      scale_color_viridis(option="viridis", discrete=TRUE) +
      scale_fill_viridis(option="viridis", discrete=TRUE)
  }
  if (full_scale == TRUE){
    plot <- plot + scale_y_continuous(limits = c(min_y, max_y), breaks = seq(floor(min_y), ceiling(max_y), scale_steps)) 
  }
  if (angle_axis_labels == TRUE){
    plot <- plot + theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
      theme(plot.margin = margin(0,0,0,40, unit = "pt"))  # pad left side of plot to read angled labels (t,r,b,l)  
  }
  plot
}

# Parallel Plot Function
# FUNCTION REF: https://stackoverflow.com/questions/52340768/using-a-custom-function-with-tidyverse 

parallel_plot <- function(df, x, y, group, viridis=TRUE, full_scale=FALSE, angle_axis_labels=FALSE) {
  x <- enquo(x)
  y <- enquo(y)
  group <- enquo(group)
  min_y <- min(df %>% pull(!!y))
  max_y <- max(df %>% pull(!!y))
  
  plot <-
    df %>%  
    ggplot(aes(x=(!!x), y=(!!y), color=(!!group), fill=(!!group), group=(!!group))) +
    stat_summary(fun.data=mean_se, geom="pointrange", position=position_dodge(0), alpha=1) +
    stat_summary(fun.data=mean_se, geom="line", position=position_dodge(0), alpha=1) +
    theme_bw()
  
  if(viridis == TRUE){
    plot <- plot +
      scale_color_viridis(option="viridis", discrete=TRUE) +
      scale_fill_viridis(option="viridis", discrete=TRUE)
  }
  if (full_scale == TRUE){
    plot <- plot + scale_y_continuous(limits = c(min_y, max_y), breaks = seq(floor(min_y), ceiling(max_y), 1)) 
  }
  if (angle_axis_labels == TRUE){
    plot <- plot + theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
      theme(plot.margin = margin(0,0,0,40, unit = "pt"))  # pad left side of plot to read angled labels (t,r,b,l)  
  }
  plot
}

# Version with different color_group
parallel_plot_color <- function(df, x, y, group, color_group, full_scale=FALSE, angle_axis_labels=FALSE) {
  x <- enquo(x)
  y <- enquo(y)
  group <- enquo(group)
  color_group <- enquo(color_group)
  min_y <- min(df %>% pull(!!y))
  max_y <- max(df %>% pull(!!y))
  
  plot <-
    df %>%  
    ggplot(aes(x=(!!x), y=(!!y), color=(!!color_group), fill=(!!color_group), group=(!!group))) +
    stat_summary(fun.data=mean_se, geom="pointrange", position=position_dodge(0), alpha=1) +
    stat_summary(fun.data=mean_se, geom="line", position=position_dodge(0), alpha=1) +
    scale_color_viridis(option="viridis", discrete=TRUE) + # <- UNCOMMENT to get colorblind-friendly palette
    theme_bw()
  
  if (full_scale == TRUE){
    plot <- plot + scale_y_continuous(limits = c(min_y, max_y), breaks = seq(floor(min_y), ceiling(max_y), 1)) 
  }
  if (angle_axis_labels == TRUE){
    plot <- plot + theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
      theme(plot.margin = margin(0,0,0,40, unit = "pt"))  # pad left side of plot to read angled labels (t,r,b,l)  
  }
  plot
}

# Violin Plot Function
# FUNCTION REF: https://stackoverflow.com/questions/52340768/using-a-custom-function-with-tidyverse 
violin_plot <- function(df, x, y, group, full_scale=FALSE, angle_axis_labels=FALSE) {
  x = enquo(x)
  y = enquo(y)
  group = enquo(group)
  min_y <- min(df %>% pull(!!y))
  max_y <- max(df %>% pull(!!y))
  
  plot <-
    df %>% group_by((!!group), (!!x)) %>% 
    ggplot(aes(x=(!!x), y=(!!y), color=(!!group), fill=(!!group)))  +
    geom_violin(alpha=0.5, position=position_dodge(0.95)) +
    geom_boxplot(fill="white", alpha=0.9, width=0.2, position=position_dodge(0.95)) +
    scale_color_viridis(option="viridis", discrete=TRUE) + # <- UNCOMMENT to get colorblind-friendly palette
    scale_fill_viridis(option="viridis", discrete=TRUE) + # <- UNCOMMENT to get colorblind-friendly palette
    theme_minimal()
  
  if (full_scale == TRUE){
    plot <- plot + scale_y_continuous(limits = c(min_y, max_y), breaks = seq(floor(min_y), ceiling(max_y), 1)) 
  }
  if (angle_axis_labels == TRUE){
    plot <- plot + theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
      theme(plot.margin = margin(0,0,0,40, unit = "pt"))  # pad left side of plot to read angled labels (t,r,b,l)  
  }
  plot
}

# Function for labelled scatterplot of variables
labeled_scatterplot <- function(df, x, y, label, group, show_points=TRUE, full_scale=FALSE, angle_axis_labels=FALSE) {
  x = enquo(x)
  y = enquo(y)
  label = enquo(label)
  group = enquo(group)
  min_y <- min(df %>% pull(!!y))
  max_y <- max(df %>% pull(!!y))
  y_range <- max_y-min_y
  
  plot <- df %>% group_by((!!group), (!!x)) %>% 
    ggplot(aes(x=(!!x), y=(!!y), color=(!!group), fill=(!!group), label=(!!label)))
  if (show_points == TRUE){
    plot <- plot + geom_point(alpha=0.7)
  }
  plot <- plot +
    geom_text(alpha=0.9, nudge_x = y_range/30, nudge_y = y_range/30) +
    scale_color_viridis(option="viridis", discrete=TRUE) + # <- UNCOMMENT to get colorblind-friendly palette
    scale_fill_viridis(option="viridis", discrete=TRUE) + # <- UNCOMMENT to get colorblind-friendly palette
    gg_theme() + theme_bw()
  
  if (full_scale == TRUE){
    plot <- plot + scale_y_continuous(limits = c(min_y, max_y), breaks = seq(floor(min_y), ceiling(max_y), 1)) 
  }
  if (angle_axis_labels == TRUE){
    plot <- plot + theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
      theme(plot.margin = margin(0,0,0,40, unit = "pt"))  # pad left side of plot to read angled labels (t,r,b,l)  
  }
  plot
}

# 3. Modelling Functions ----
# Function to get linear model output and pairwise comparisons

# LM Output Comparisons Function
# **Reference Code:** 
# - https://cran.r-project.org/web/packages/emmeans/vignettes/comparisons.html 
# - https://broom.tidymodels.org/reference/tidy.summary_emm.html 

lm_emms_pairs_condition <- function(df, formula){
  # run linear model
  lm_out <- lm(formula, data=df)
  print( summary(lm_out) )
  print( lm_df <- tidy(lm_out) )
  
  # get marginal averages (estimated marginal means / Least-squares means)
  emms <- emmeans(lm_out, "Condition")
  print( emms_df <- tidy(emms, conf.int = TRUE) )
  
  # get contrasts
  # (?) tidy(contrast(emms)) # contrast from grand mean(?)
  # pwcs = contrast between paired groups; equivalent to: contrast(emms, method="pairwise") 
  #   +  bonferroni adjusted for multiple comparisons
  pwcs <- tidy(pairs(emms)) %>% mutate(bfrn.adj.p.value = tidy(pairs(emms, adjust="bonferroni")) %>% pull(adj.p.value))
  print(pwcs)
  
  # get effect sizes
  print( tidy(eff_size(emms, sigma = sigma(lm_out), edf = Inf)) )
  
  # plot confidence intervals
  #Option 1
  print( plot(emms, comparisons = TRUE))
  #Option 2
  confint_plot <- ggplot(emms_df, aes(Condition, estimate)) +
    geom_point() + geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width=0.5) + gg_theme()
  print( confint_plot )
}

lm_emms_pairs_persona <- function(df, formula){
  # run linear model
  lm_out <- lm(formula, data=df)
  print( summary(lm_out) )
  print( lm_df <- tidy(lm_out) )
  
  # get marginal averages (estimated marginal means / Least-squares means)
  emms <- emmeans(lm_out, "Persona_Group")
  print( emms_df <- tidy(emms, conf.int = TRUE) )
  
  # get contrasts
  # (?) tidy(contrast(emms)) # contrast from grand mean(?)
  # pwcs = contrast between paired groups; equivalent to: contrast(emms, method="pairwise") 
  #   +  bonferroni adjusted for multiple comparisons
  pwcs <- tidy(pairs(emms)) %>% mutate(bfrn.adj.p.value = tidy(pairs(emms, adjust="bonferroni")) %>% pull(adj.p.value))
  print(pwcs)
  
  # get effect sizes
  print( tidy(eff_size(emms, sigma = sigma(lm_out), edf = Inf)) )
  
  # plot confidence intervals
  #Option 1
  print( plot(emms, comparisons = TRUE))
  #Option 2
  confint_plot <- ggplot(emms_df, aes(Persona_Group, estimate)) +
    geom_point() + geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width=0.5) + gg_theme()
  print( confint_plot )
}

# Output:
# (1) LM summary, (2) tidy LM, (3) EMMs w/ CIs, (4) Pairwise comp, (5) Effect sizes*, (6) EMM comp plot, (7) EMM CI plot
# (*) not currently sure about the `edf` parameter, currently speifying Inf, narrowing confint unrealistically


