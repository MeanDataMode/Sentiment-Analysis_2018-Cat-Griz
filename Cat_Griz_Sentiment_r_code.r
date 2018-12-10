#
# Sentiment Analysis
#
# By Anthony Layton (Tony Layton)
#
# This file will create a high-resolution chart
# depicting the 2018 Montana vs. Montana State Rivalry Football game
#


# Import Librarys
library(ggplot2)
library(scales)
library(dplyr)
library(readr)
library(ggthemes)


# Import Data File
d <- read_delim("Cat_Griz_Sentiment.txt", "\t",
                escape_double = FALSE, 
                col_types = cols(Date_Time = col_number(),
                                 score = col_number()), 
                trim_ws = TRUE)


# Remove 'Others' from the data.
# Others are defined as twitter users that follow both UM and MSU
#   or twitter users that do not follow UM or MSU
d <- subset(x = d, subset = d$Team != 'Others')


# get the minimum and maximum for the 'annotate' feature within the chart
ma <- max(d$Score)
mi <- min(d$Score)
offset_l <- -.35
offset_r <- 1.1
time_font_size <- 2.5
label_font_size <- 2

# Produce the chart
the_plot <- ggplot(d, aes(x=Date_Time,y=Score, group = Team, colour = Team)) +
    # Select Chart Theme
    theme_bw() +
    # Add School Colors to Lines
    scale_color_manual(values=c('Maroon', 'blue')) +
    # Feature - Chart labels
    labs(x="Time (Mountain Time Zone)",
         y="Fan Sentiment",
         title="Sentiment of the 2018 Montana vs. Montana State",
         subtitle = expression(paste(italic("(analysis based on tweets posted on Twitter during the game)"))),
         caption = expression(paste(italic("Graphique de Tony Layton")))) +
    theme(plot.subtitle=element_text(size=7, hjust=.45, face="italic", color="#404040")) +
    # Feature - x axis markers and labels
    scale_x_continuous(breaks = c(120000, 130000, 140000, 150000, 160000, 170000),
                       labels = c('12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM')) +

    # Game Time Features
    # Feature - Grey Box indicating Game Play
    annotate("rect", xmin = 121130, xmax = 133651, ymin = mi, ymax = ma, alpha = .2) +
    annotate("rect", xmin = 135920, xmax = 152058, ymin = mi, ymax = ma, alpha = .2) +
    # Feature - Game Starts Line and Text
    geom_vline(xintercept=121130, colour="black") +
    geom_text(aes(x=121130, label="Kickoff", y=160), 
              size=time_font_size, 
              colour="black", 
              angle=90, 
              vjust = offset_l) +
    # Feature - Start of Second Quarter Line and Text
    geom_vline(xintercept=124605, colour="black") +
    geom_text(aes(x=124605, label="Start Q2", y=160), 
              size=time_font_size, 
              colour="black", 
              angle=90, 
              vjust = offset_l) +
    # Feature - Start of Third Quarter Line and Text
    geom_vline(xintercept=135920, colour="black") +
    geom_text(aes(x=135920, label="Start Q3", y=160), 
              size=time_font_size, 
              colour="black", 
              angle=90, 
              vjust = offset_l) +
    # Feature - Start of Fourth Quarter Line and Text
    geom_vline(xintercept=142941, colour="black") +
    geom_text(aes(x=142941, label="Start Q4", y=160), 
              size=time_font_size, 
              colour="black", 
              angle=90, 
              vjust = offset_l) +
    # Feature - Game Ends Line and Text
    geom_vline(xintercept=152058, colour="black") +
    geom_text(aes(x=152058, label="Game Ends", y=160), 
              size=time_font_size, 
              colour="black", 
              angle=90, 
              vjust = offset_r) +
    
    # Game Scores Features
    # Feature - Griz Touchdown (7-0) Line and Text
    geom_vline(xintercept=121610, colour="palevioletred") +
    geom_text(aes(x=121610, label="UM Touchdown", y=325), 
              size=label_font_size, 
              colour="palevioletred", 
              angle=90, 
              vjust = offset_r) +
    # Feature - Griz Touchdown (14-0) Line and Text
    geom_vline(xintercept=130712, colour="palevioletred") +
    geom_text(aes(x=130712, label="UM Touchdown", y=325), 
              size=label_font_size, 
              colour="palevioletred", 
              angle=90, 
              vjust = offset_l) +
    # Feature - Griz Touchdown (22-0) Line and Text
    geom_vline(xintercept=131142, colour="palevioletred") +
    geom_text(aes(x=131142, label="UM Touchdown", y=325), 
              size=label_font_size, 
              colour="palevioletred", 
              angle=90, 
              vjust = offset_r) +
    # Feature - Bobcat Touchdown (22-7) Line and Text
    geom_vline(xintercept=133628, colour="steelblue1") +
    geom_text(aes(x=133628, label="MSU Touchdown", y=325), 
              size=label_font_size, 
              colour="steelblue1", 
              angle=90, 
              vjust = offset_r) +
    # Feature - Bobcat Touchdown (22-15) Line and Text
    geom_vline(xintercept=143347, colour="steelblue1") +
    geom_text(aes(x=143347, label="MSU Touchdown", y=325), 
              size=label_font_size, 
              colour="steelblue1", 
              angle=90, 
              vjust = offset_r) +
    # Feature - Griz FG (25-15) Line and Text
    geom_vline(xintercept=144945, colour="palevioletred") +
    geom_text(aes(x=144945, label="UM Field Goal", y=325), 
              size=label_font_size, 
              colour="palevioletred", 
              angle=90, 
              vjust = offset_l) +
    # Feature - Bobcat Touchdown (25-22) Line and Text
    geom_vline(xintercept=145612, colour="steelblue1") +
    geom_text(aes(x=145612, label="MSU Touchdown", y=325), 
              size=label_font_size, 
              colour="steelblue1", 
              angle=90, 
              vjust = offset_r) +
    # Feature - Bobcat Touchdown (25-29) Line and Text
    geom_vline(xintercept=150918, colour="steelblue1") +
    geom_text(aes(x=150918, label="MSU Touchdown", y=325), 
              size=label_font_size, 
              colour="steelblue1", 
              angle=90, 
              vjust = offset_l) +
    
    # Sentiment Line
    geom_line() +
    # Feature - smoothing line
    stat_smooth(se=F, geom = 'line', alpha = 0.6, size=1)

# Save the chart
ggsave("2018_Cat_Griz.jpg", 
       plot = the_plot, 
       device = "jpg", 
       path = NULL,
       scale = 1, 
       width = 8, 
       height = 6, 
       units = "in",
       dpi = 600, 
       limitsize = FALSE)

# Save the chart large
ggsave("2018_Cat_Griz_large.jpg", 
       plot = the_plot, 
       device = "jpg", 
       path = NULL,
       scale = 1, 
       width = 60, 
       height = 40, 
       units = "in",
       dpi = 600, 
       limitsize = FALSE)
