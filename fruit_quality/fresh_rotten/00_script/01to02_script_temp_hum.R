# ---------------------------------------------------------------------------------------
#
# Description       : The code provided is designed to generate a series of graphs
#                     using the data in folder N°01 and to synthesise the statistical data into an HTML 
#                     
# Authors           : PAVIET-SALOMON Yvanne <yvanne.paviet-salomon@inrae.fr>
# 
# Creation date     : 2024-06-15 10:50:54.110367
# Modification date : [1] "2024-09-08 08:42:19 CEST"

# Command specification for file modification date for traceability
# fichier_info <- file.info("C:/01_R_data_paper_mangoes/00_script/01to02_script_temp_hum.R")
# date_modification <- fichier_info$mtime
# print(date_modification)
# 
# Comments          : This script has specific graph generation functions and statistical analysis.
#
# create_temp_hum_graphic_summary() > Function to create the average (+ optional min and max ) temperature graph and relative humidity graph
# create_temp_graphic_summary() > Function to create the average (+ optional min and max ) temperature graph
# create_temp_hum_graphic () > Function to create the overall temperature and relative humidity graph
# create_temp_graphic () > Function to create the overall temperature graph

# ---------------------------------------------------------------------------------------

create_temp_hum_graphic_summary <- function(graphic_file, indices_files, 
                                            average_graph_T_Air, min_graph_T_Air, max_graph_T_Air, 
                                            average_graph_T_mangoes, min_graph_T_mangoes, max_graph_T_mangoes, 
                                            average_graph_RH_Air, min_graph_RH_Air, max_graph_RH_Air) {
  # Checking that all arguments are provided and are not empty
  args <- list(indices_files, average_graph_T_Air, min_graph_T_Air, max_graph_T_Air, 
               average_graph_T_mangoes, min_graph_T_mangoes, max_graph_T_mangoes, 
               average_graph_RH_Air, min_graph_RH_Air, max_graph_RH_Air)
  
  if (any(sapply(args, is.null)) || any(sapply(args, length) == 0)) {
    stop("One or more arguments are empty or missing.")
  }
  
  # Checking that all vectors have the same length
  lengths <- sapply(args, length)
  if (length(unique(lengths)) != 1) {
    stop("All vectors must have the same length.")
  }
  
  base_name <- tools::file_path_sans_ext(basename(graphic_file))
  
  # Open the output PNG file
  png(filename = graphic_file, width = 1200, height = 854, res = 150)
  
  # Use the actual time values from indices_files
  adjusted_indices <- c(time_values_list[indices_files])
  adjusted_indices <- unlist(adjusted_indices)
  adjusted_indices <- as.POSIXct(adjusted_indices, format = "%d/%m/%Y %H:%M")
  print(adjusted_indices)
  
  # Create a vector of sequential indices
  seq_indices <- seq_along(adjusted_indices) -1
  
  # Calculate intermediate positions for min and max
  middle_indices <- adjusted_indices[-length(adjusted_indices)] + diff(adjusted_indices) / 2
  
  # Adjust margins
  par(mar = c(5, 4, 4, 5)) 
  
  # Determine y-axis limits for temperatures
  #y_limits <- range(c(average_graph_T_Air, min_graph_T_Air, max_graph_T_Air, 
  #                   average_graph_T_mangoes, min_graph_T_mangoes, max_graph_T_mangoes))
  
  # Determine y-axis limits for temperatures
  y_limits <- range(c(average_graph_T_Air, average_graph_T_mangoes))
  y_limits[2] <- y_limits[2] + 1
  draw_segments <- function(x, y, col, lty = 1) {
    # Draw the horizontal and vertical segments for each step
    for (i in 1:(length(x) - 1)) {
      # horizontal Segment 
      segments(x[i], y[i], x[i + 1], y[i], col = col, lty = lty, lwd = 2.5)
      
      # vertical Segment
      if (i < length(x) - 1) {
        segments(x[i + 1], y[i], x[i + 1], y[i + 1], col = col, lty = lty, lwd = 2.5)
      }
    }
    
    # Extend the last horizontal segment
    extended_time <- x[length(x)] + 3600
    segments(x[length(x)], y[length(y)], extended_time, y[length(y)], col = col, lty = lty, lwd = 2.5)
    
    # Add the final vertical segment to reach the y value of the previous point
    if (length(x) > 1) {
      segments(x[length(x)], y[length(y)], x[length(x)], y[length(y) - 1], col = col, lty = lty, lwd = 2.5)
    }
    
    # Optional: Add a dot to indicate the end
    points(extended_time, y[length(y)], col = col, pch = 19)
  }
  
  # Initialize the graph for temperatures (mangoes)
  plot(adjusted_indices, average_graph_T_mangoes, type = "n", 
       ylim = y_limits, 
       ylab = "", xlab = "", # Remove axis labels
       main = paste("Average Air Temperature/Relative humidity and Average Mango Temperature\n", base_name),
       axes = FALSE)
  print(adjusted_indices)
  print(average_graph_T_mangoes)
  #Add segments for mango temperatures
  draw_segments(adjusted_indices, average_graph_T_mangoes, "red")
  
  #Add segments for air temperatures
  draw_segments(adjusted_indices, average_graph_T_Air, "red", lty = 2)
  
  #Optional
  #Add points for min and max mango temperatures in the middle of step
  #points(middle_indices, min_graph_T_mangoes[-length(min_graph_T_mangoes)], type = "p", pch = 20, col = "orange")
  #points(middle_indices, max_graph_T_mangoes[-length(max_graph_T_mangoes)], type = "p", pch = 20, col = "orange")
  
  # Add points for min and max air temperatures in the middle of phases
  #points(middle_indices, min_graph_T_Air[-length(min_graph_T_Air)], type = "p", pch = 20, col = "red")
  #points(middle_indices, max_graph_T_Air[-length(max_graph_T_Air)], type = "p", pch = 20, col = "red")
  
  # Add axis outlines and detail y-axis values for temperatures
  axis(2, at = seq(floor(min(y_limits)), ceiling(max(y_limits)), by = 1), 
       cex.axis = 0.7) 
  box()
  
  # Add the step axis with sequential indices
  axis(1, at = adjusted_indices, labels = seq_indices) 
  
  # Add step labels
  mtext("Step number", side = 1, line = 2)
  
  # Add temperature labels
  mtext("Temperature (°C)", side = 2, line = 2)
  
  # Add the second data series for humidity
  par(new = TRUE)
  plot(adjusted_indices, average_graph_RH_Air, type = "n",
       ylim = range(c(average_graph_RH_Air, min_graph_RH_Air, max_graph_RH_Air)), 
       ylab = "", xlab = "", axes = FALSE)
  draw_segments(adjusted_indices, average_graph_RH_Air, "blue")
  
  #Optional
  # Add points for min and max air relative humidity in the middle of step
  #points(middle_indices, min_graph_RH_Air[-length(min_graph_RH_Air)], type = "p", pch = 1, col = "blue")
  #points(middle_indices, max_graph_RH_Air[-length(max_graph_RH_Air)], type = "p", pch = 1, col = "blue")
  
  # Add axes for relative humidity
  axis(4, las = 1)
  mtext("Relative Humidity (%)", side = 4, line = 3)
  
  # Two-column legend
  legend("top", # Position and adjustment of the legend
         legend = c(
           "Average Mango Temperature",
           "Average Air Temperature",
           "Average Air Relative Humidity"
           #Optional > select "bottom" with inset = (0,-0,3)
           #"Min/Max Temperature of Mangoes",
           #"Min/Max Temperature of Air",
           #"Min/Max Relative Humidity of Air"
         ), 
         col = c("red", "red", "blue", "orange", "red", "blue"), 
         #Optional
         #lty = c(1, 1, 1, NA, NA, NA), 
         #pch = c(NA, NA, NA, 20, 20, 1), 
         lty = c(1, 2, 1, NA, NA, NA),
         lwd = c(2, 2, 2, NA, NA, NA), # Line width
         cex = 0.7, pt.cex = 1.2, bty = "n", # Text and point size, without box
         ncol = 3 # Number of columns in the legend
  )
  
  # Close the PNG file
  dev.off()
  Sys.sleep(0.1)
} #end

create_temp_graphic_summary <- function(graphic_file, indices_files, 
                                        average_graph_T_Air, min_graph_T_Air, max_graph_T_Air, 
                                        average_graph_T_mangoes, min_graph_T_mangoes, max_graph_T_mangoes) {
  base_name <- tools::file_path_sans_ext(basename(graphic_file))
  
  # Open the output png file
  png(filename = graphic_file, width = 1200, height = 854, res = 150)
  
  ## Use the actual time values from indices_files
  adjusted_indices <- c(time_values_list[indices_files])
  adjusted_indices <- unlist(adjusted_indices)
  adjusted_indices <- as.POSIXct(adjusted_indices, format = "%d/%m/%Y %H:%M")
  
  # Create a vector of sequential indice 
  seq_indices <- seq_along(adjusted_indices) -1
  
  
  # Calculate intermediate position for min and max
  middle_indices <- adjusted_indices[-length(adjusted_indices)] + diff(adjusted_indices) / 2
  
  
  # Adjust margins
  par( mar = c(6, 4, 4, 5)) 
  
  # Determine y-axis limits for temperature 
  # y_limits <- range(c(average_graph_T_Air, min_graph_T_Air, max_graph_T_Air, 
  #                    average_graph_T_mangoes, min_graph_T_mangoes, max_graph_T_mangoes))
  
  y_limits <- range(c(average_graph_T_Air, average_graph_T_mangoes))
  y_limits[2] <- y_limits[2] + 1
  
  # Function to draw horizontal ans vertical segment for each step
  draw_segments <- function(x, y, col, lty = 1) {
    # Draw the horizontal and vertical segments for each step
    for (i in 1:(length(x) - 1)) {
      # Horizontal Segment 
      segments(x[i], y[i], x[i + 1], y[i], col = col, lty = lty, lwd = 2.5)
      
      # Vertical Segment 
      if (i < length(x) - 1) {
        segments(x[i + 1], y[i], x[i + 1], y[i + 1], col = col, lty = lty, lwd = 2.5)
      }
    }
    
    # Extend the last horizontal segment
    extended_time <- x[length(x)] + 3600
    segments(x[length(x)], y[length(y)], extended_time, y[length(y)], col = col, lty = lty, lwd = 2.5)
    
    # Add the final vertical segment to reach the y value of the previous point
    if (length(x) > 1) {
      segments(x[length(x)], y[length(y)], x[length(x)], y[length(y) - 1], col = col, lty = lty, lwd = 2.5)
    }
    
    # Optional: Add a dot to indicate the end
    points(extended_time, y[length(y)], col = col, pch = 19)
  }
  
  
  # Temperature plot
  plot(adjusted_indices, average_graph_T_mangoes, type = "n", 
       ylim = y_limits, 
       ylab = "", xlab = "",
       main = paste("Average Air and Mango Temperatures\n", base_name),
       axes = FALSE)
  
  # Add segments for mango temperatures
  draw_segments(adjusted_indices, average_graph_T_mangoes, "red")
  
  # Add segments for air temperatures
  draw_segments(adjusted_indices, average_graph_T_Air, "red", lty = 2)
  
  # Add points for min and max mangoes temperatures in the middle of step
  # points(middle_indices, min_graph_T_mangoes[-length(min_graph_T_mangoes)], type = "p", pch = 20, col = "orange")
  # points(middle_indices, max_graph_T_mangoes[-length(max_graph_T_mangoes)], type = "p", pch = 20, col = "orange")
  
  # Add points for min and max air temperatures in the middle of step
  # points(middle_indices, min_graph_T_Air[-length(min_graph_T_Air)], type = "p", pch = 20, col = "red")
  # points(middle_indices, max_graph_T_Air[-length(max_graph_T_Air)], type = "p", pch = 20, col = "red")
  
  # Add axis outlines and detail y-axis values for temperatures
  axis(2, at = seq(floor(min(y_limits)), ceiling(max(y_limits)), by = 1), 
       cex.axis = 0.7)
  box()
  
  # Add axis step
  axis(1, at = adjusted_indices, labels = seq_indices)
  
  # Add label step
  mtext("Step Number", side = 1, line = 2)
  
  # add temperature label
  mtext("Temperature (°C)", side = 2, line = 2)
  
  # legend with two colums
  legend("top", # Position and adjustment of the legend
         legend = c(
           "Average Mango Temperature",
           "Average Air Temperature"
           #Optional > select "bottom" with inset = (0,-0,3)
           #"Min/Max Temperature of Mangoes (orange, points)",
           #"Min/Max Temperature of Air (red, points)"
         ), 
         col = c("red", "red", "orange", "red"), 
         lty = c(1, 2, NA, NA), 
         lwd = c(2, 2, NA, NA), # Line width
         #pch = c(NA, NA, 20, 20),
         cex = 0.7, pt.cex = 1.2, bty = "n", 
         ncol = 2 
  )
  
  # Close png file
  dev.off()
  Sys.sleep(0.1)
  
} #end

create_temp_hum_graphic <- function(data, graphic_file) {
  # Convert time to POSIXct format
  data$Time_conversion <- as.POSIXct(data$Time, format = "%d/%m/%Y %H:%M")
  
  # Generate smoothed curves
  smooth_mangoes <- smooth.spline(data$Time_conversion, data$T_mangoes)
  smooth_air <- smooth.spline(data$Time_conversion, data$T_Air)
  smooth_humidity <- smooth.spline(data$Time_conversion, data$RH_Air)
  
  # Determine y-axis limits for temperature
  y_limits <- range(c(data$T_mangoes, data$T_Air))
  
  # Open the output png file
  png(filename = graphic_file, width = 1200, height = 854, res = 150)
  base_name <- tools::file_path_sans_ext(basename(graphic_file))
  
  # Create the main plot for temperature and relative humidity
  par(mar = c(5, 4, 4, 4) + 0.1)
  plot(data$Time_conversion, data$T_mangoes, xlab = NA, ylab = NA, type = "n", main = paste("Air Temperature/Relative Humidity and Mango Temperature \n", base_name), ylim = y_limits, axes = FALSE)
  lines(smooth_mangoes, col = "red", lwd = 2.5)
  lines(smooth_air, col = "red", lty = 2, lwd = 2)
  axis(2, at = seq(floor(min(y_limits)), ceiling(max(y_limits)), by = 1), cex.axis = 0.7, col = "black", col.axis = "black")
  mtext("Temperature (°C)", side = 2, line = 2, cex = 1.2)
  axis.POSIXct(1, at = seq(min(data$Time_conversion), max(data$Time_conversion), by = "hours"), format = "%m/%d %Hh", las = 2, cex.axis = 0.7)
  
  # Overlay humidity data
  par(new = TRUE, mar = c(5, 4, 4, 4) + 0.1)
  plot(data$Time_conversion, data$RH_Air, type = "n", xaxt = "n", yaxt = "n", xlab = "", ylab = "", xlim = range(data$Time_conversion), ylim = range(data$RH_Air))
  lines(smooth_humidity, col="blue", lwd = 2.5)
  axis(4, ylim = range(data$RH_Air), cex.axis = 1.2)
  mtext("Relative Humidity (%)", side = 4, line = 2, cex = 1.2)
  
  # Add legend

  legend("topright",
         legend = c(
           "Temperature of mangoes", 
           "Temperature of air", 
           "Relative Humidity"
         ), 
         col = c("red", "red", "blue"), 
         lty = c(1, 2, 1),
         cex = 0.8, pt.cex = 1.2, bty = "n", 
  )
  
  
  #Close the output png file
  dev.off()
  Sys.sleep(0.1)
}

#-----------------------END OF create_temp_hum_graphic(arg1,arg2)--------------


# Function to create the overall temperature and relative humidity graph

create_temp_graphic <- function(data, graphic_file) {
  # Convert time to POSIXct format
  data$Time_conversion <- as.POSIXct(data$Time, format = "%d/%m/%Y %H:%M")
  base_name <- tools::file_path_sans_ext(basename(graphic_file))
  
  # Generate smoothed curves
  smooth_mangoes <- smooth.spline(data$Time_conversion, data$T_mangoes)
  smooth_air <- smooth.spline(data$Time_conversion, data$T_Air)
  
  # Determine y-axis limits for temperature
  y_limits <- range(c(data$T_mangoes, data$T_Air))
  
  # Open output png file
  png(filename = graphic_file, width = 1200, height = 854, res = 150)
  
  # Create the main plot for temperature
  par(mar = c(5, 4, 4, 4) + 0.1)
  plot(data$Time_conversion, data$T_mangoes, xlab = NA, ylab = NA, type = "n", 
       main = paste("Air Temperature and Mango Temperature\n", base_name), ylim = y_limits, axes = FALSE)
  lines(smooth_mangoes, col = "red", lwd = 2.5)
  lines(smooth_air, col = "red", lty = 2, lwd = 2.5)
  axis(2, at = seq(floor(min(y_limits)), ceiling(max(y_limits)), by = 1), 
       cex.axis = 0.7)
  mtext("Temperature (°C)", side = 2, line = 2, cex = 1.2)
  axis.POSIXct(1, at = seq(min(data$Time_conversion), max(data$Time_conversion), by = "hours"), 
               format = "%m/%d %Hh", las = 2, cex.axis = 0.7)
  box()
  # Add legend
  
  legend("topright",
         legend = c(
           "Mangoes Temperature", 
           "Air Temperature"
         ), 
         col = c("red", "red"), 
         lty = c(1, 2),
         cex = 0.8, pt.cex = 1.2, bty = "n", 
  )
  
  # Close the output png file
  dev.off()
  Sys.sleep(0.1)
}

#-----------------------Beginning Of assign_graph_values_temp_hum(arg1,arg2,arg3)--------------


assign_graph_values_temp_hum <- function(indices_files, column_stats, txt_files) {
  # Initialize lists for the values
  average_graph_T_mangoes <- numeric(length(indices_files))
  min_graph_T_mangoes <- numeric(length(indices_files))
  max_graph_T_mangoes <- numeric(length(indices_files))
  average_graph_T_Air <- numeric(length(indices_files))
  min_graph_T_Air <- numeric(length(indices_files))
  max_graph_T_Air <- numeric(length(indices_files))
  average_graph_RH_Air <- numeric(length(indices_files))
  min_graph_RH_Air <- numeric(length(indices_files))
  max_graph_RH_Air <- numeric(length(indices_files))
  
  # Iterate through the file indices and assign the values
  for (i in seq_along(indices_files)) {
    average_graph_T_mangoes[i] <- column_stats[[txt_files[indices_files[i]]]]$T_mangoes$average
    min_graph_T_mangoes[i] <- column_stats[[txt_files[indices_files[i]]]]$T_mangoes$min
    max_graph_T_mangoes[i] <- column_stats[[txt_files[indices_files[i]]]]$T_mangoes$max
    average_graph_T_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$T_Air$average
    min_graph_T_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$T_Air$min
    max_graph_T_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$T_Air$max
    average_graph_RH_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$RH_Air$average
    min_graph_RH_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$RH_Air$min
    max_graph_RH_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$RH_Air$max
  }
  
  return(list(
    average_graph_T_mangoes = average_graph_T_mangoes,
    min_graph_T_mangoes = min_graph_T_mangoes,
    max_graph_T_mangoes = max_graph_T_mangoes,
    average_graph_T_Air = average_graph_T_Air,
    min_graph_T_Air = min_graph_T_Air,
    max_graph_T_Air = max_graph_T_Air,
    average_graph_RH_Air = average_graph_RH_Air,
    min_graph_RH_Air = min_graph_RH_Air,
    max_graph_RH_Air = max_graph_RH_Air
  ))
}

#-----------------------Beginning Of assign_graph_values_temp(arg1,arg2,arg3)--------------

assign_graph_values_temp <- function(indices_files, column_stats, txt_files) {
  # Initialize lists for the values
  average_graph_T_mangoes <- numeric(length(indices_files))
  min_graph_T_mangoes <- numeric(length(indices_files))
  max_graph_T_mangoes <- numeric(length(indices_files))
  average_graph_T_Air <- numeric(length(indices_files))
  min_graph_T_Air <- numeric(length(indices_files))
  max_graph_T_Air <- numeric(length(indices_files))
  
  # Iterate through the file indices and assign the values
  for (i in seq_along(indices_files)) {
    average_graph_T_mangoes[i] <- column_stats[[txt_files[indices_files[i]]]]$T_mangoes$average
    min_graph_T_mangoes[i] <- column_stats[[txt_files[indices_files[i]]]]$T_mangoes$min
    max_graph_T_mangoes[i] <- column_stats[[txt_files[indices_files[i]]]]$T_mangoes$max
    average_graph_T_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$T_Air$average
    min_graph_T_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$T_Air$min
    max_graph_T_Air[i] <- column_stats[[txt_files[indices_files[i]]]]$T_Air$max
  }
  
  return(list(
    average_graph_T_mangoes = average_graph_T_mangoes,
    min_graph_T_mangoes = min_graph_T_mangoes,
    max_graph_T_mangoes = max_graph_T_mangoes,
    average_graph_T_Air = average_graph_T_Air,
    min_graph_T_Air = min_graph_T_Air,
    max_graph_T_Air = max_graph_T_Air
  ))
}

# Function to extract the numbers in order to sort
extract_numbers_pattern <- function(file) {
  basename_file <- basename(file)

  # extract numbers
  match <- regexpr("([0-9]+)_([0-9]+)_([0-9]+)", basename(file))
  # if match
  if (match[1] != -1) {
    # convert 
    number_str <- regmatches(basename_file, match)
    numbers <- as.numeric(unlist(strsplit(number_str, "_")))
    
    if (length(numbers) == 3) {
      return(numbers)
    } else {
      return(c(NA, NA, NA))
    }
  } else {
    return(c(NA, NA, NA))
  }
}

# ----------------------------- path definition-------------

# IMPORTANT: Before running this script, set the working directory to the path where your R script is located.
# Replace "C:/R_analyse/00_script" with the correct path on your computer.
# This ensures that all file paths used in the script are relative to this directory.

# Example for Windows:
# setwd("C:/your/path/to/script")

# Example for Mac or Linux:
# setwd("/your/path/to/script")

# Set the working directory
setwd("C:/01_R_data_paper_mangoes/00_script")

# source directory
path_src_box_temp <- "../01_src_subset_dataset_T_H"

# result directory
path_res_box_temp <- "../02_res_subset_dataset_T_H"

# ----------------------------- package loading

library(stats)      # for statistical functions
library(utils)      # for utility functions (e.g., read.csv, write.csv)
library(graphics)   # for basic graphical functions
library(grDevices)  # for graphical devices
library(datasets)   # for built-in datasets
library(methods)    # for formal methods and classes
library(base)       # for the base R system functions (loaded by default)

# Check if the packages are installed and install them if they are not
required_packages <- c("utils", "graphics", "grDevices", "datasets", "methods")

for (pkg in required_packages) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg, dependencies = TRUE)
    library(pkg, character.only = TRUE)
  }
}

# ----------------------------- data loading

# Retrieve the names of .txt files
txt_files <- list.files(path = path_src_box_temp, pattern = "\\.txt$", full.names = TRUE)

# Extraire les numéros pour chaque fichier
numbers <- t(sapply(txt_files, extract_numbers_pattern))

# Convertir les numéros en un format de tri numérique
# Cela transforme chaque triplet de numéros en une séquence unique pour le tri
numeric_order <- apply(numbers, 1, function(x) x[1] * 10000 + x[2] * 100 + x[3])

# Trier les fichiers en fonction des numéros extraits
txt_files_sorted <- txt_files[order(numeric_order)]

# Afficher la liste des fichiers triés
print(txt_files_sorted)

# Create a list to store the matrices
matrices_list <- list()

# Read each file and store it in a matrix
for (file in txt_files_sorted) {
  try({
    # Read the file as a data frame
    data <- read.table(file, header = TRUE, sep = "\t", stringsAsFactors = FALSE)
    
    # Convert the data frame to a matrix, excluding the date column
    data_matrix <- as.matrix(data[, -1])  # The date column is the first one
    
    # Add the matrix to the list
    matrices_list[[file]] <- data_matrix
  }, silent = TRUE)
}

# Initialize a list to store time values
time_values_list <- list()

for (file in txt_files_sorted) {
  try({
    # Read the file as a data frame
    data <- read.table(file, header = TRUE, sep = "\t", stringsAsFactors = FALSE)
    
    # Extract the first value from the time column (the first column)
    first_time_value <- data[1, 1]  # The first element of the first column
    
    # Add this value to the list
    time_values_list[[file]] <- first_time_value
  }, silent = TRUE)
}

# ----------------------------- Generating HTML Report

# Create a list to store the statistics
column_stats <- list()

# Calculate statistics for each matrix in matrices_list
for (file in names(matrices_list)) {
  # Access the matrix
  data_matrix <- matrices_list[[file]]
  
  # Initialize a list to store statistics for each column
  stats <- list()
  
  # Loop through each numeric column
  for (col in 1:ncol(data_matrix)) {
    # Extract the column data
    column_data <- as.numeric(data_matrix[, col])
    
    # Check if the column contains numeric data
    if (!any(is.na(column_data))) {
      # Calculate the statistics
      column_stats_col <- list(
        average = round(mean(column_data), 2),
        min = min(column_data),
        max = max(column_data),
        sd = round(sd(column_data), 2),
        var = round(var(column_data), 2)
      )
    } else {
      # If the column contains missing values, assign NA to all statistics
      column_stats_col <- list(average = NA, min = NA, max = NA, sd = NA, var = NA)
    }
    
    # Add the statistics to the list
    stats[[colnames(data_matrix)[col]]] <- column_stats_col
  }
  
  # Add the matrix statistics to the main list
  column_stats[[file]] <- stats
}


# Define the full path for the HTML file
html_file_path <- file.path(path_res_box_temp, "statistics.html")

# Open the HTML file for writing
html_file <- file(html_file_path, "w")

# Start writing HTML code
writeLines("<!DOCTYPE html>", html_file)
writeLines("<html>", html_file)
writeLines("<head>", html_file)
writeLines("<title>File Statistics</title>", html_file)
writeLines("</head>", html_file)
writeLines("<body>", html_file)

# Start the table
writeLines("<table border='1'>", html_file)

# Table header
writeLines("<tr>", html_file)
writeLines("<th>Source File</th>", html_file)
writeLines("<th>average T mangoes</th>", html_file)
writeLines("<th>Min T mangoes</th>", html_file)
writeLines("<th>Max T mangoes</th>", html_file)
writeLines("<th>SD T mangoes</th>", html_file)
writeLines("<th>Variance T mangoes</th>", html_file)
writeLines("<th>average T air</th>", html_file)
writeLines("<th>Min T air</th>", html_file)
writeLines("<th>Max T air</th>", html_file)
writeLines("<th>SD T air</th>", html_file)
writeLines("<th>Variance T air</th>", html_file)
writeLines("<th>average Relative Humidity air</th>", html_file)
writeLines("<th>Min Realtive Humidity air</th>", html_file)
writeLines("<th>Max Relative Humidity air</th>", html_file)
writeLines("<th>SD Relative Humidity air</th>", html_file)
writeLines("<th>Variance Relative Humidity air</th>", html_file)
writeLines("</tr>", html_file)

# Add table data
for (file in names(column_stats)) {
  stats <- column_stats[[file]]
  writeLines("<tr>", html_file)
  writeLines(paste0("<td>", file, "</td>"), html_file)
  for (stat_name in names(stats)) {
    stat <- stats[[stat_name]]
    writeLines(paste0("<td>", stat$average, "</td>"), html_file)
    writeLines(paste0("<td>", stat$min, "</td>"), html_file)
    writeLines(paste0("<td>", stat$max, "</td>"), html_file)
    writeLines(paste0("<td>", stat$sd, "</td>"), html_file)
    writeLines(paste0("<td>", stat$var, "</td>"), html_file)
  }
  writeLines("</tr>", html_file)
}

# Finish the table and the body of the HTML page
writeLines("</table>", html_file)
writeLines("</body>", html_file)
writeLines("</html>", html_file)

# Close the HTML file
close(html_file)

##-----------------------------Generating txt et csv

# Create a list to store the statistics data frames
stats_data_frames <- list()

# Transform the lists of statistics into data frames
for (file in names(column_stats)) {
  # Access the statistics for this file
  stats <- column_stats[[file]]
  
  # Initialize vectors to store the statistics
  column_names <- names(stats)
  averages <- sapply(stats, function(x) x$average)
  mins <- sapply(stats, function(x) x$min)
  maxs <- sapply(stats, function(x) x$max)
  sds <- sapply(stats, function(x) x$sd)
  vars <- sapply(stats, function(x) x$var)
  
  # Create a data frame for the statistics of this file
  stats_df <- data.frame(
    File = rep(file, length(column_names)),
    Column = column_names,
    Average = averages,
    Min = mins,
    Max = maxs,
    SD = sds,
    Var = vars,
    stringsAsFactors = FALSE
  )
  
  # Add this data frame to the list
  stats_data_frames[[file]] <- stats_df
}

# Combine all the data frames into one
combined_stats_df <- do.call(rbind, stats_data_frames)

# Full path for the CSV and TXT files
csv_file_path <- file.path(path_res_box_temp, "combined_statistics.csv")
txt_file_path <- file.path(path_res_box_temp, "combined_statistics.txt")

# Write the statistics to a CSV file
write.csv(combined_stats_df, csv_file_path, row.names = FALSE)

# Write the statistics to a TXT file
write.table(combined_stats_df, txt_file_path, sep = "\t", row.names = FALSE, quote = FALSE)

print("CSV and TXT files have been created successfully.")

##------Beginning of Generating General Graphics----------

# Définir le motif pour capturer tous les fichiers .txt
pattern <- "00_All_Recording_Packing_House_to_Arrival_At_INRAE.*\\.txt"

# Lister tous les fichiers qui correspondent au motif dans le dossier
files <- list.files(path = path_src_box_temp, pattern = pattern, full.names = TRUE)

# Extraire les numéros pour chaque fichier
numbers <- t(sapply(files, extract_numbers_pattern))

# Convertir les numéros en un format de tri numérique
# Cela transforme chaque triplet de numéros en une séquence unique pour le tri
numeric_order <- apply(numbers, 1, function(x) x[1] * 10000 + x[2] * 100 + x[3])

# Trier les fichiers en fonction des numéros extraits
txt_src_files_graphic <- files[order(numeric_order)]

# Read data from each specified file into separate data frames
box_1_1_1 <- read.table(txt_src_files_graphic[1], header=TRUE, sep="\t")
box_1_1_7 <- read.table(txt_src_files_graphic[2], header=TRUE, sep="\t")
box_1_1_12 <- read.table(txt_src_files_graphic[3], header=TRUE, sep="\t")
box_1_3_1 <- read.table(txt_src_files_graphic[4], header=TRUE, sep="\t")
box_1_3_7 <- read.table(txt_src_files_graphic[5], header=TRUE, sep="\t")
box_1_3_12 <- read.table(txt_src_files_graphic[6], header=TRUE, sep="\t")
box_1_4_1 <- read.table(txt_src_files_graphic[7], header=TRUE, sep="\t")
box_1_4_7 <- read.table(txt_src_files_graphic[8], header=TRUE, sep="\t")
box_1_4_12 <- read.table(txt_src_files_graphic[9], header=TRUE, sep="\t")
box_2_1_1 <- read.table(txt_src_files_graphic[10], header=TRUE, sep="\t")
box_2_1_7 <- read.table(txt_src_files_graphic[11], header=TRUE, sep="\t")
box_2_1_12 <- read.table(txt_src_files_graphic[12], header=TRUE, sep="\t")
box_2_2_1 <- read.table(txt_src_files_graphic[13], header=TRUE, sep="\t")
box_2_2_3 <- read.table(txt_src_files_graphic[14], header=TRUE, sep="\t")
box_2_2_6 <- read.table(txt_src_files_graphic[15], header=TRUE, sep="\t")
box_2_2_10 <- read.table(txt_src_files_graphic[16], header=TRUE, sep="\t")
box_2_2_12 <- read.table(txt_src_files_graphic[17], header=TRUE, sep="\t")
box_2_4_1 <- read.table(txt_src_files_graphic[18], header=TRUE, sep="\t")
box_2_4_7 <- read.table(txt_src_files_graphic[19], header=TRUE, sep="\t")
box_3_1_12 <- read.table(txt_src_files_graphic[20], header=TRUE, sep="\t")
box_3_2_1 <- read.table(txt_src_files_graphic[21], header=TRUE, sep="\t")
box_3_2_3 <- read.table(txt_src_files_graphic[22], header=TRUE, sep="\t")
box_3_2_7 <- read.table(txt_src_files_graphic[23], header=TRUE, sep="\t")
box_3_2_10 <- read.table(txt_src_files_graphic[24], header=TRUE, sep="\t")
box_3_3_12 <- read.table(txt_src_files_graphic[25], header=TRUE, sep="\t")
box_4_1_1 <- read.table(txt_src_files_graphic[26], header=TRUE, sep="\t")
box_4_1_7 <- read.table(txt_src_files_graphic[27], header=TRUE, sep="\t")
box_4_2_1 <- read.table(txt_src_files_graphic[28], header=TRUE, sep="\t")
box_4_2_7 <- read.table(txt_src_files_graphic[29], header=TRUE, sep="\t")
box_4_4_1 <- read.table(txt_src_files_graphic[30], header=TRUE, sep="\t")
box_4_4_7 <- read.table(txt_src_files_graphic[31], header=TRUE, sep="\t")

box_1_1_1_graphic <- file.path(path_res_box_temp, "Box_1_1_1.png")
box_1_1_7_graphic <- file.path(path_res_box_temp, "Box_1_1_7.png")
box_1_1_12_graphic <- file.path(path_res_box_temp, "Box_1_1_12.png")
box_1_3_1_graphic <- file.path(path_res_box_temp, "Box_1_3_1.png")
box_1_3_7_graphic <- file.path(path_res_box_temp, "Box_1_3_7.png")
box_1_3_12_graphic <- file.path(path_res_box_temp, "Box_1_3_12.png")
box_1_4_1_graphic <- file.path(path_res_box_temp, "Box_1_4_1.png")
box_1_4_7_graphic <- file.path(path_res_box_temp, "Box_1_4_7.png")
box_1_4_12_graphic <- file.path(path_res_box_temp, "Box_1_4_12.png")
box_2_1_1_graphic <- file.path(path_res_box_temp, "Box_2_1_1.png")
box_2_1_7_graphic <- file.path(path_res_box_temp, "Box_2_1_7.png")
box_2_1_12_graphic <- file.path(path_res_box_temp, "Box_2_1_12.png")
box_2_2_1_graphic <- file.path(path_res_box_temp, "Box_2_2_1.png")
box_2_2_3_graphic <- file.path(path_res_box_temp, "Box_2_2_3.png")
box_2_2_6_graphic <- file.path(path_res_box_temp, "Box_2_2_6.png")
box_2_2_10_graphic <- file.path(path_res_box_temp, "Box_2_2_10.png")
box_2_2_12_graphic <- file.path(path_res_box_temp, "Box_2_2_12.png")
box_2_4_1_graphic <- file.path(path_res_box_temp, "Box_2_4_1.png")
box_2_4_7_graphic <- file.path(path_res_box_temp, "Box_2_4_7.png")
box_3_1_12_graphic <- file.path(path_res_box_temp, "Box_3_1_12.png")
box_3_2_1_graphic <- file.path(path_res_box_temp, "Box_3_2_1.png")
box_3_2_3_graphic <- file.path(path_res_box_temp, "Box_3_2_3.png")
box_3_2_7_graphic <- file.path(path_res_box_temp, "Box_3_2_7.png")
box_3_2_10_graphic <- file.path(path_res_box_temp, "Box_3_2_10.png")
box_3_3_12_graphic <- file.path(path_res_box_temp, "Box_3_3_12.png")
box_4_1_1_graphic <- file.path(path_res_box_temp, "Box_4_1_1.png")
box_4_1_7_graphic <- file.path(path_res_box_temp, "Box_4_1_7.png")
box_4_2_1_graphic <- file.path(path_res_box_temp, "Box_4_2_1.png")
box_4_2_7_graphic <- file.path(path_res_box_temp, "Box_4_2_7.png")
box_4_4_1_graphic <- file.path(path_res_box_temp, "Box_4_4_1.png")
box_4_4_7_graphic <- file.path(path_res_box_temp, "Box_4_4_7.png")

create_temp_hum_graphic(box_1_1_1, box_1_1_1_graphic)
create_temp_hum_graphic(box_1_1_7, box_1_1_7_graphic)
create_temp_hum_graphic(box_1_1_12, box_1_1_12_graphic)
create_temp_graphic(box_1_3_1, box_1_3_1_graphic)
create_temp_graphic(box_1_3_7, box_1_3_7_graphic)
create_temp_graphic(box_1_3_12, box_1_3_12_graphic)
create_temp_hum_graphic(box_1_4_1, box_1_4_1_graphic)
create_temp_graphic(box_1_4_7, box_1_4_7_graphic)
create_temp_graphic(box_1_4_12, box_1_4_12_graphic)
create_temp_graphic(box_2_1_1, box_2_1_1_graphic)
create_temp_graphic(box_2_1_7, box_2_1_7_graphic)
create_temp_graphic(box_2_1_12, box_2_1_12_graphic)
create_temp_hum_graphic(box_2_2_1, box_2_2_1_graphic)
create_temp_graphic(box_2_2_3, box_2_2_3_graphic)
create_temp_hum_graphic(box_2_2_6, box_2_2_6_graphic)
create_temp_graphic(box_2_2_10, box_2_2_10_graphic)
create_temp_hum_graphic(box_2_2_12, box_2_2_12_graphic)
create_temp_graphic(box_2_4_1, box_2_4_1_graphic)
create_temp_graphic(box_2_4_7, box_2_4_7_graphic)
create_temp_graphic(box_3_1_12, box_3_1_12_graphic)
create_temp_graphic(box_3_2_1, box_3_2_1_graphic)
create_temp_graphic(box_3_2_3, box_3_2_3_graphic)
create_temp_graphic(box_3_2_7, box_3_2_7_graphic)
create_temp_graphic(box_3_2_10, box_3_2_10_graphic)
create_temp_graphic(box_3_3_12, box_3_3_12_graphic)
create_temp_hum_graphic(box_4_1_1, box_4_1_1_graphic)
create_temp_graphic(box_4_1_7, box_4_1_7_graphic)
create_temp_graphic(box_4_2_1, box_4_2_1_graphic)
create_temp_graphic(box_4_2_7, box_4_2_7_graphic)
create_temp_hum_graphic(box_4_4_1, box_4_4_1_graphic)
create_temp_graphic(box_4_4_7, box_4_4_7_graphic)

##------End of Generating general Graphics----------

##------Beginning of Generating step Graphics----------

# Indices of text files for the different areas # format windows -> sort to do due to x_x_xx

# indices_files_1 <- c(1, 63, 94, 125, 156, 187, 218, 249, 280, 311)
# indices_files_2 <- c(1+1, 63+1, 94+1, 125+1, 156+1, 187+1, 218+1, 249+1, 280+1, 311+1)
# indices_files_3 <- c(1+2, 63+2, 94+2, 125+2, 156+2, 187+2, 218+2, 249+2, 280+2, 311+2)
# indices_files_4 <- c(1+3, 63+3, 94+3, 125+3, 156+3, 187+3, 218+3, 249+3, 280+3, 311+3)
# indices_files_5 <- c(1+4, 63+4, 94+4, 125+4, 156+4, 187+4, 218+4, 249+4, 280+4, 311+4)
# indices_files_6 <- c(1+5, 63+5, 94+5, 125+5, 156+5, 187+5, 218+5, 249+5, 280+5, 311+5)
# indices_files_7 <- c(1+6, 63+6, 94+6, 125+6, 156+6, 187+6, 218+6, 249+6, 280+6, 311+6)
# indices_files_8 <- c(1+7, 63+7, 94+7, 125+7, 156+7, 187+7, 218+7, 249+7, 280+7, 311+7)
# indices_files_9 <- c(1+8, 63+8, 94+8, 125+8, 156+8, 187+8, 218+8, 249+8, 280+8, 311+8)
# indices_files_10 <- c(1+9, 63+9, 94+9, 125+9, 156+9, 187+9, 218+9, 249+9, 280+9, 311+9)
# indices_files_11 <- c(1+10, 63+10, 94+10, 125+10, 156+10, 187+10, 218+10, 249+10, 280+10, 311+10)
# indices_files_12 <- c(1+11, 63+11, 94+11, 125+11, 156+11, 187+11, 218+11, 249+11, 280+11, 311+11)
# indices_files_13 <- c(1+12, 63+12, 94+12, 125+12, 156+12, 187+12, 218+12, 249+12, 280+12, 311+12)
# indices_files_14 <- c(1+13, 63+13, 94+13, 125+13, 156+13, 187+13, 218+13, 249+13, 280+13, 311+13)
# indices_files_15 <- c(1+14, 63+14, 94+14, 125+14, 156+14, 187+14, 218+14, 249+14, 280+14, 311+14)
# indices_files_16 <- c(1+15, 63+15, 94+15, 125+15, 156+15, 187+15, 218+15, 249+15, 280+15, 311+15)
# indices_files_17 <- c(1+16, 63+16, 94+16, 125+16, 156+16, 187+16, 218+16, 249+16, 280+16, 311+16)
# indices_files_18 <- c(1+17, 63+17, 94+17, 125+17, 156+17, 187+17, 218+17, 249+17, 280+17, 311+17)
# indices_files_19 <- c(1+18, 63+18, 94+18, 125+18, 156+18, 187+18, 218+18, 249+18, 280+18, 311+18)
# indices_files_20 <- c(1+19, 63+19, 94+19, 125+19, 156+19, 187+19, 218+19, 249+19, 280+19, 311+19)
# indices_files_21 <- c(1+20, 63+20, 94+20, 125+20, 156+20, 187+20, 218+20, 249+20, 280+20, 311+20)
# indices_files_22 <- c(1+21, 63+21, 94+21, 125+21, 156+21, 187+21, 218+21, 249+21, 280+21, 311+21)
# indices_files_23 <- c(1+22, 63+22, 94+22, 125+22, 156+22, 187+22, 218+22, 249+22, 280+22, 311+22)
# indices_files_24 <- c(1+23, 63+23, 94+23, 125+23, 156+23, 187+23, 218+23, 249+23, 280+23, 311+23)
# indices_files_25 <- c(1+24, 63+24, 94+24, 125+24, 156+24, 187+24, 218+24, 249+24, 280+24, 311+24)
# indices_files_26 <- c(1+25, 63+25, 94+25, 125+25, 156+25, 187+25, 218+25, 249+25, 280+25, 311+25)
# indices_files_27 <- c(1+26, 63+26, 94+26, 125+26, 156+26, 187+26, 218+26, 249+26, 280+26, 311+26)
# indices_files_28 <- c(1+27, 63+27, 94+27, 125+27, 156+27, 187+27, 218+27, 249+27, 280+27, 311+27)
# indices_files_29 <- c(1+28, 63+28, 94+28, 125+28, 156+28, 187+28, 218+28, 249+28, 280+28, 311+28)
# indices_files_30 <- c(1+29, 63+29, 94+29, 125+29, 156+29, 187+29, 218+29, 249+29, 280+29, 311+29)
# indices_files_31 <- c(1+30, 63+30, 94+30, 125+30, 156+30, 187+30, 218+30, 249+30, 280+30, 341)

indices_1 <- 1:11
indices_2 <- 12:22
indices_3 <- 23:33
indices_4 <- 34:44
indices_5 <- 45:55
indices_6 <- 56:66
indices_7 <- 67:77
indices_8 <- 78:88
indices_9 <- 89:99
indices_10 <- 100:110
indices_11 <- 111:121
indices_12 <- 122:132
indices_13 <- 133:143
indices_14 <- 144:154
indices_15 <- 155:165
indices_16 <- 166:176
indices_17 <- 177:187
indices_18 <- 188:198
indices_19 <- 199:209
indices_20 <- 210:220
indices_21 <- 221:231
indices_22 <- 232:242
indices_23 <- 243:253
indices_24 <- 254:264
indices_25 <- 265:275
indices_26 <- 276:286
indices_27 <- 287:297
indices_28 <- 298:308
indices_29 <- 309:319
indices_30 <- 320:330
indices_31 <- 331:341 #end

indices_files_1 <- c(1, 3:11)
indices_files_2 <- c(12, 14:22)
indices_files_3 <- c(23, 25:33)
indices_files_4 <- c(34, 36:44)
indices_files_5 <- c(45, 47:55)
indices_files_6 <- c(56, 58:66)
indices_files_7 <- c(67, 69:77)
indices_files_8 <- c(78, 80:88)
indices_files_9 <- c(89, 91:99)
indices_files_10 <- c(100, 102:110)
indices_files_11 <- c(111, 113:121)
indices_files_12 <- c(122, 124:132)
indices_files_13 <- c(133, 135:143)
indices_files_14 <- c(144, 146:154)
indices_files_15 <- c(155, 157:165)
indices_files_16 <- c(166, 168:176)
indices_files_17 <- c(177, 179:187)
indices_files_18 <- c(188, 190:198)
indices_files_19 <- c(199, 201:209)
indices_files_20 <- c(210, 212:220)
indices_files_21 <- c(221, 223:231)
indices_files_22 <- c(232, 234:242)
indices_files_23 <- c(243, 245:253)
indices_files_24 <- c(254, 256:264)
indices_files_25 <- c(265, 267:275)
indices_files_26 <- c(276, 278:286)
indices_files_27 <- c(287, 289:297)
indices_files_28 <- c(298, 300:308)
indices_files_29 <- c(309, 311:319)
indices_files_30 <- c(320, 322:330)
indices_files_31 <- c(331, 333:341)
  
# Define the paths for graphic files
box_1_1_1_graphic_summary <- file.path(path_res_box_temp, "Box_1_1_1_Step_Number.png")
box_1_1_7_graphic_summary <- file.path(path_res_box_temp, "Box_1_1_7_Step_Number.png")
box_1_1_12_graphic_summary <- file.path(path_res_box_temp, "Box_1_1_12_Step_Number.png")
box_1_3_1_graphic_summary <- file.path(path_res_box_temp, "Box_1_3_1_Step_Number.png")
box_1_3_7_graphic_summary <- file.path(path_res_box_temp, "Box_1_3_7_Step_Number.png")
box_1_3_12_graphic_summary <- file.path(path_res_box_temp, "Box_1_3_12_Step_Number.png")
box_1_4_1_graphic_summary <- file.path(path_res_box_temp, "Box_1_4_1_Step_Number.png")
box_1_4_7_graphic_summary <- file.path(path_res_box_temp, "Box_1_4_7_Step_Number.png")
box_1_4_12_graphic_summary <- file.path(path_res_box_temp, "Box_1_4_12_Step_Number.png")
box_2_1_1_graphic_summary <- file.path(path_res_box_temp, "Box_2_1_1_Step_Number.png")
box_2_1_7_graphic_summary <- file.path(path_res_box_temp, "Box_2_1_7_Step_Number.png")
box_2_1_12_graphic_summary <- file.path(path_res_box_temp, "Box_2_1_12_Step_Number.png")
box_2_2_1_graphic_summary <- file.path(path_res_box_temp, "Box_2_2_1_Step_Number.png")
box_2_2_3_graphic_summary <- file.path(path_res_box_temp, "Box_2_2_3_Step_Number.png")
box_2_2_6_graphic_summary <- file.path(path_res_box_temp, "Box_2_2_6_Step_Number.png")
box_2_2_10_graphic_summary <- file.path(path_res_box_temp, "Box_2_2_10_Step_Number.png")
box_2_2_12_graphic_summary <- file.path(path_res_box_temp, "Box_2_2_12_Step_Number.png")
box_2_4_1_graphic_summary <- file.path(path_res_box_temp, "Box_2_4_1_Step_Number.png")
box_2_4_7_graphic_summary <- file.path(path_res_box_temp, "Box_2_4_7_Step_Number.png")
box_3_1_12_graphic_summary <- file.path(path_res_box_temp, "Box_3_1_12_Step_Number.png")
box_3_2_1_graphic_summary <- file.path(path_res_box_temp, "Box_3_2_1_Step_Number.png")
box_3_2_3_graphic_summary <- file.path(path_res_box_temp, "Box_3_2_3_Step_Number.png")
box_3_2_7_graphic_summary <- file.path(path_res_box_temp, "Box_3_2_7_Step_Number.png")
box_3_2_10_graphic_summary <- file.path(path_res_box_temp, "Box_3_2_10_Step_Number.png")
box_3_3_12_graphic_summary <- file.path(path_res_box_temp, "Box_3_3_12_Step_Number.png")
box_4_1_1_graphic_summary <- file.path(path_res_box_temp, "Box_4_1_1_Step_Number.png")
box_4_1_7_graphic_summary <- file.path(path_res_box_temp, "Box_4_1_7_Step_Number.png")
box_4_2_1_graphic_summary <- file.path(path_res_box_temp, "Box_4_2_1_Step_Number.png")
box_4_2_7_graphic_summary <- file.path(path_res_box_temp, "Box_4_2_7_Step_Number.png")
box_4_4_1_graphic_summary <- file.path(path_res_box_temp, "Box_4_4_1_Step_Number.png")
box_4_4_7_graphic_summary <- file.path(path_res_box_temp, "Box_4_4_7_Step_Number.png")

# Use the function assign_graph_values_temp_hum()
graph_values_1 <- assign_graph_values_temp_hum(indices_files_1, column_stats, txt_files_sorted)
graph_values_2 <- assign_graph_values_temp_hum(indices_files_2, column_stats, txt_files_sorted)
graph_values_3 <- assign_graph_values_temp_hum(indices_files_3, column_stats, txt_files_sorted)
graph_values_4 <- assign_graph_values_temp(indices_files_4, column_stats, txt_files_sorted)
graph_values_5 <- assign_graph_values_temp(indices_files_5, column_stats, txt_files_sorted)
graph_values_6 <- assign_graph_values_temp(indices_files_6, column_stats, txt_files_sorted)
graph_values_7 <- assign_graph_values_temp_hum(indices_files_7, column_stats, txt_files_sorted)
graph_values_8 <- assign_graph_values_temp(indices_files_8, column_stats, txt_files_sorted)
graph_values_9 <- assign_graph_values_temp(indices_files_9, column_stats, txt_files_sorted)
graph_values_10 <- assign_graph_values_temp(indices_files_10, column_stats, txt_files_sorted)
graph_values_11 <- assign_graph_values_temp(indices_files_11, column_stats, txt_files_sorted)
graph_values_12 <- assign_graph_values_temp(indices_files_12, column_stats, txt_files_sorted)
graph_values_13 <- assign_graph_values_temp_hum(indices_files_13, column_stats, txt_files_sorted)
graph_values_14 <- assign_graph_values_temp(indices_files_14, column_stats, txt_files_sorted)
graph_values_15 <- assign_graph_values_temp_hum(indices_files_15, column_stats, txt_files_sorted)
graph_values_16 <- assign_graph_values_temp(indices_files_16, column_stats, txt_files_sorted)
graph_values_17 <- assign_graph_values_temp_hum(indices_files_17, column_stats, txt_files_sorted)
graph_values_18 <- assign_graph_values_temp(indices_files_18, column_stats, txt_files_sorted)
graph_values_19 <- assign_graph_values_temp(indices_files_19, column_stats, txt_files_sorted)
graph_values_20 <- assign_graph_values_temp(indices_files_20, column_stats, txt_files_sorted)
graph_values_21 <- assign_graph_values_temp(indices_files_21, column_stats, txt_files_sorted)
graph_values_22 <- assign_graph_values_temp(indices_files_22, column_stats, txt_files_sorted)
graph_values_23 <- assign_graph_values_temp(indices_files_23, column_stats, txt_files_sorted)
graph_values_24 <- assign_graph_values_temp(indices_files_24, column_stats, txt_files_sorted)
graph_values_25 <- assign_graph_values_temp(indices_files_25, column_stats, txt_files_sorted)
graph_values_26 <- assign_graph_values_temp_hum(indices_files_26, column_stats, txt_files_sorted)
graph_values_27 <- assign_graph_values_temp(indices_files_27, column_stats, txt_files_sorted)
graph_values_28 <- assign_graph_values_temp(indices_files_28, column_stats, txt_files_sorted)
graph_values_29 <- assign_graph_values_temp(indices_files_29, column_stats, txt_files_sorted)
graph_values_30 <- assign_graph_values_temp_hum(indices_files_30, column_stats, txt_files_sorted)
graph_values_31 <- assign_graph_values_temp(indices_files_31, column_stats, txt_files_sorted)


# Extract the assigned values

average_graph_T_mangoes_1 <- graph_values_1$average_graph_T_mangoes
min_graph_T_mangoes_1 <- graph_values_1$min_graph_T_mangoes
max_graph_T_mangoes_1 <- graph_values_1$max_graph_T_mangoes
average_graph_T_Air_1 <- graph_values_1$average_graph_T_Air
min_graph_T_Air_1 <- graph_values_1$min_graph_T_Air
max_graph_T_Air_1 <- graph_values_1$max_graph_T_Air
average_graph_RH_Air_1 <- graph_values_1$average_graph_RH_Air
min_graph_RH_Air_1 <- graph_values_1$min_graph_RH_Air
max_graph_RH_Air_1 <- graph_values_1$max_graph_RH_Air

average_graph_T_mangoes_2 <- graph_values_2$average_graph_T_mangoes
min_graph_T_mangoes_2 <- graph_values_2$min_graph_T_mangoes
max_graph_T_mangoes_2 <- graph_values_2$max_graph_T_mangoes
average_graph_T_Air_2 <- graph_values_2$average_graph_T_Air
min_graph_T_Air_2 <- graph_values_2$min_graph_T_Air
max_graph_T_Air_2 <- graph_values_2$max_graph_T_Air
average_graph_RH_Air_2 <- graph_values_2$average_graph_RH_Air
min_graph_RH_Air_2 <- graph_values_2$min_graph_RH_Air
max_graph_RH_Air_2 <- graph_values_2$max_graph_RH_Air

average_graph_T_mangoes_3 <- graph_values_3$average_graph_T_mangoes
min_graph_T_mangoes_3 <- graph_values_3$min_graph_T_mangoes
max_graph_T_mangoes_3 <- graph_values_3$max_graph_T_mangoes
average_graph_T_Air_3 <- graph_values_3$average_graph_T_Air
min_graph_T_Air_3 <- graph_values_3$min_graph_T_Air
max_graph_T_Air_3 <- graph_values_3$max_graph_T_Air
average_graph_RH_Air_3 <- graph_values_3$average_graph_RH_Air
min_graph_RH_Air_3 <- graph_values_3$min_graph_RH_Air
max_graph_RH_Air_3 <- graph_values_3$max_graph_RH_Air

average_graph_T_mangoes_4 <- graph_values_4$average_graph_T_mangoes
min_graph_T_mangoes_4 <- graph_values_4$min_graph_T_mangoes
max_graph_T_mangoes_4 <- graph_values_4$max_graph_T_mangoes
average_graph_T_Air_4 <- graph_values_4$average_graph_T_Air
min_graph_T_Air_4 <- graph_values_4$min_graph_T_Air
max_graph_T_Air_4 <- graph_values_4$max_graph_T_Air

average_graph_T_mangoes_5 <- graph_values_5$average_graph_T_mangoes
min_graph_T_mangoes_5 <- graph_values_5$min_graph_T_mangoes
max_graph_T_mangoes_5 <- graph_values_5$max_graph_T_mangoes
average_graph_T_Air_5 <- graph_values_5$average_graph_T_Air
min_graph_T_Air_5 <- graph_values_5$min_graph_T_Air
max_graph_T_Air_5 <- graph_values_5$max_graph_T_Air

average_graph_T_mangoes_6 <- graph_values_6$average_graph_T_mangoes
min_graph_T_mangoes_6 <- graph_values_6$min_graph_T_mangoes
max_graph_T_mangoes_6 <- graph_values_6$max_graph_T_mangoes
average_graph_T_Air_6 <- graph_values_6$average_graph_T_Air
min_graph_T_Air_6 <- graph_values_6$min_graph_T_Air
max_graph_T_Air_6 <- graph_values_6$max_graph_T_Air

average_graph_T_mangoes_7 <- graph_values_7$average_graph_T_mangoes
min_graph_T_mangoes_7 <- graph_values_7$min_graph_T_mangoes
max_graph_T_mangoes_7 <- graph_values_7$max_graph_T_mangoes
average_graph_T_Air_7 <- graph_values_7$average_graph_T_Air
min_graph_T_Air_7 <- graph_values_7$min_graph_T_Air
max_graph_T_Air_7 <- graph_values_7$max_graph_T_Air
average_graph_RH_Air_7 <- graph_values_7$average_graph_RH_Air
min_graph_RH_Air_7 <- graph_values_7$min_graph_RH_Air
max_graph_RH_Air_7 <- graph_values_7$max_graph_RH_Air

average_graph_T_mangoes_8 <- graph_values_8$average_graph_T_mangoes
min_graph_T_mangoes_8 <- graph_values_8$min_graph_T_mangoes
max_graph_T_mangoes_8 <- graph_values_8$max_graph_T_mangoes
average_graph_T_Air_8 <- graph_values_8$average_graph_T_Air
min_graph_T_Air_8 <- graph_values_8$min_graph_T_Air
max_graph_T_Air_8 <- graph_values_8$max_graph_T_Air

average_graph_T_mangoes_9 <- graph_values_9$average_graph_T_mangoes
min_graph_T_mangoes_9 <- graph_values_9$min_graph_T_mangoes
max_graph_T_mangoes_9 <- graph_values_9$max_graph_T_mangoes
average_graph_T_Air_9 <- graph_values_9$average_graph_T_Air
min_graph_T_Air_9 <- graph_values_9$min_graph_T_Air
max_graph_T_Air_9 <- graph_values_9$max_graph_T_Air

average_graph_T_mangoes_10 <- graph_values_10$average_graph_T_mangoes
min_graph_T_mangoes_10 <- graph_values_10$min_graph_T_mangoes
max_graph_T_mangoes_10 <- graph_values_10$max_graph_T_mangoes
average_graph_T_Air_10 <- graph_values_10$average_graph_T_Air
min_graph_T_Air_10 <- graph_values_10$min_graph_T_Air
max_graph_T_Air_10 <- graph_values_10$max_graph_T_Air

average_graph_T_mangoes_11 <- graph_values_11$average_graph_T_mangoes
min_graph_T_mangoes_11 <- graph_values_11$min_graph_T_mangoes
max_graph_T_mangoes_11 <- graph_values_11$max_graph_T_mangoes
average_graph_T_Air_11 <- graph_values_11$average_graph_T_Air
min_graph_T_Air_11 <- graph_values_11$min_graph_T_Air
max_graph_T_Air_11 <- graph_values_11$max_graph_T_Air

average_graph_T_mangoes_12 <- graph_values_12$average_graph_T_mangoes
min_graph_T_mangoes_12 <- graph_values_12$min_graph_T_mangoes
max_graph_T_mangoes_12 <- graph_values_12$max_graph_T_mangoes
average_graph_T_Air_12 <- graph_values_12$average_graph_T_Air
min_graph_T_Air_12 <- graph_values_12$min_graph_T_Air
max_graph_T_Air_12 <- graph_values_12$max_graph_T_Air

average_graph_T_mangoes_13 <- graph_values_13$average_graph_T_mangoes
min_graph_T_mangoes_13 <- graph_values_13$min_graph_T_mangoes
max_graph_T_mangoes_13 <- graph_values_13$max_graph_T_mangoes
average_graph_T_Air_13 <- graph_values_13$average_graph_T_Air
min_graph_T_Air_13 <- graph_values_13$min_graph_T_Air
max_graph_T_Air_13 <- graph_values_13$max_graph_T_Air
average_graph_RH_Air_13 <- graph_values_13$average_graph_RH_Air
min_graph_RH_Air_13 <- graph_values_13$min_graph_RH_Air
max_graph_RH_Air_13 <- graph_values_13$max_graph_RH_Air

average_graph_T_mangoes_14 <- graph_values_14$average_graph_T_mangoes
min_graph_T_mangoes_14 <- graph_values_14$min_graph_T_mangoes
max_graph_T_mangoes_14 <- graph_values_14$max_graph_T_mangoes
average_graph_T_Air_14 <- graph_values_14$average_graph_T_Air
min_graph_T_Air_14 <- graph_values_14$min_graph_T_Air
max_graph_T_Air_14 <- graph_values_14$max_graph_T_Air


average_graph_T_mangoes_15 <- graph_values_15$average_graph_T_mangoes
min_graph_T_mangoes_15 <- graph_values_15$min_graph_T_mangoes
max_graph_T_mangoes_15 <- graph_values_15$max_graph_T_mangoes
average_graph_T_Air_15 <- graph_values_15$average_graph_T_Air
min_graph_T_Air_15 <- graph_values_15$min_graph_T_Air
max_graph_T_Air_15 <- graph_values_15$max_graph_T_Air
average_graph_RH_Air_15 <- graph_values_15$average_graph_RH_Air
min_graph_RH_Air_15 <- graph_values_15$min_graph_RH_Air
max_graph_RH_Air_15 <- graph_values_15$max_graph_RH_Air

average_graph_T_mangoes_16 <- graph_values_16$average_graph_T_mangoes
min_graph_T_mangoes_16 <- graph_values_16$min_graph_T_mangoes
max_graph_T_mangoes_16 <- graph_values_16$max_graph_T_mangoes
average_graph_T_Air_16 <- graph_values_16$average_graph_T_Air
min_graph_T_Air_16 <- graph_values_16$min_graph_T_Air
max_graph_T_Air_16 <- graph_values_16$max_graph_T_Air

average_graph_T_mangoes_17 <- graph_values_17$average_graph_T_mangoes
min_graph_T_mangoes_17 <- graph_values_17$min_graph_T_mangoes
max_graph_T_mangoes_17 <- graph_values_17$max_graph_T_mangoes
average_graph_T_Air_17 <- graph_values_17$average_graph_T_Air
min_graph_T_Air_17 <- graph_values_17$min_graph_T_Air
max_graph_T_Air_17 <- graph_values_17$max_graph_T_Air
average_graph_RH_Air_17 <- graph_values_17$average_graph_RH_Air
min_graph_RH_Air_17 <- graph_values_17$min_graph_RH_Air
max_graph_RH_Air_17 <- graph_values_17$max_graph_RH_Air

average_graph_T_mangoes_18 <- graph_values_18$average_graph_T_mangoes
min_graph_T_mangoes_18 <- graph_values_18$min_graph_T_mangoes
max_graph_T_mangoes_18 <- graph_values_18$max_graph_T_mangoes
average_graph_T_Air_18 <- graph_values_18$average_graph_T_Air
min_graph_T_Air_18 <- graph_values_18$min_graph_T_Air
max_graph_T_Air_18 <- graph_values_18$max_graph_T_Air

average_graph_T_mangoes_19 <- graph_values_19$average_graph_T_mangoes
min_graph_T_mangoes_19 <- graph_values_19$min_graph_T_mangoes
max_graph_T_mangoes_19 <- graph_values_19$max_graph_T_mangoes
average_graph_T_Air_19 <- graph_values_19$average_graph_T_Air
min_graph_T_Air_19 <- graph_values_19$min_graph_T_Air
max_graph_T_Air_19 <- graph_values_19$max_graph_T_Air

average_graph_T_mangoes_20 <- graph_values_20$average_graph_T_mangoes
min_graph_T_mangoes_20 <- graph_values_20$min_graph_T_mangoes
max_graph_T_mangoes_20 <- graph_values_20$max_graph_T_mangoes
average_graph_T_Air_20 <- graph_values_20$average_graph_T_Air
min_graph_T_Air_20 <- graph_values_20$min_graph_T_Air
max_graph_T_Air_20 <- graph_values_20$max_graph_T_Air

average_graph_T_mangoes_21 <- graph_values_21$average_graph_T_mangoes
min_graph_T_mangoes_21 <- graph_values_21$min_graph_T_mangoes
max_graph_T_mangoes_21 <- graph_values_21$max_graph_T_mangoes
average_graph_T_Air_21 <- graph_values_21$average_graph_T_Air
min_graph_T_Air_21 <- graph_values_21$min_graph_T_Air
max_graph_T_Air_21 <- graph_values_21$max_graph_T_Air

average_graph_T_mangoes_22 <- graph_values_22$average_graph_T_mangoes
min_graph_T_mangoes_22 <- graph_values_22$min_graph_T_mangoes
max_graph_T_mangoes_22 <- graph_values_22$max_graph_T_mangoes
average_graph_T_Air_22 <- graph_values_22$average_graph_T_Air
min_graph_T_Air_22 <- graph_values_22$min_graph_T_Air
max_graph_T_Air_22 <- graph_values_22$max_graph_T_Air

average_graph_T_mangoes_23 <- graph_values_23$average_graph_T_mangoes
min_graph_T_mangoes_23 <- graph_values_23$min_graph_T_mangoes
max_graph_T_mangoes_23 <- graph_values_23$max_graph_T_mangoes
average_graph_T_Air_23 <- graph_values_23$average_graph_T_Air
min_graph_T_Air_23 <- graph_values_23$min_graph_T_Air
max_graph_T_Air_23 <- graph_values_23$max_graph_T_Air

average_graph_T_mangoes_24 <- graph_values_24$average_graph_T_mangoes
min_graph_T_mangoes_24 <- graph_values_24$min_graph_T_mangoes
max_graph_T_mangoes_24 <- graph_values_24$max_graph_T_mangoes
average_graph_T_Air_24 <- graph_values_24$average_graph_T_Air
min_graph_T_Air_24 <- graph_values_24$min_graph_T_Air
max_graph_T_Air_24 <- graph_values_24$max_graph_T_Air

average_graph_T_mangoes_25 <- graph_values_25$average_graph_T_mangoes
min_graph_T_mangoes_25 <- graph_values_25$min_graph_T_mangoes
max_graph_T_mangoes_25 <- graph_values_25$max_graph_T_mangoes
average_graph_T_Air_25 <- graph_values_25$average_graph_T_Air
min_graph_T_Air_25 <- graph_values_25$min_graph_T_Air
max_graph_T_Air_25 <- graph_values_25$max_graph_T_Air

average_graph_T_mangoes_26 <- graph_values_26$average_graph_T_mangoes
min_graph_T_mangoes_26 <- graph_values_26$min_graph_T_mangoes
max_graph_T_mangoes_26 <- graph_values_26$max_graph_T_mangoes
average_graph_T_Air_26 <- graph_values_26$average_graph_T_Air
min_graph_T_Air_26 <- graph_values_26$min_graph_T_Air
max_graph_T_Air_26 <- graph_values_26$max_graph_T_Air
average_graph_RH_Air_26 <- graph_values_26$average_graph_RH_Air
min_graph_RH_Air_26 <- graph_values_26$min_graph_RH_Air
max_graph_RH_Air_26 <- graph_values_26$max_graph_RH_Air

average_graph_T_mangoes_27 <- graph_values_27$average_graph_T_mangoes
min_graph_T_mangoes_27 <- graph_values_27$min_graph_T_mangoes
max_graph_T_mangoes_27 <- graph_values_27$max_graph_T_mangoes
average_graph_T_Air_27 <- graph_values_27$average_graph_T_Air
min_graph_T_Air_27 <- graph_values_27$min_graph_T_Air
max_graph_T_Air_27 <- graph_values_27$max_graph_T_Air

average_graph_T_mangoes_28 <- graph_values_28$average_graph_T_mangoes
min_graph_T_mangoes_28 <- graph_values_28$min_graph_T_mangoes
max_graph_T_mangoes_28 <- graph_values_28$max_graph_T_mangoes
average_graph_T_Air_28 <- graph_values_28$average_graph_T_Air
min_graph_T_Air_28 <- graph_values_28$min_graph_T_Air
max_graph_T_Air_28 <- graph_values_28$max_graph_T_Air

average_graph_T_mangoes_29 <- graph_values_29$average_graph_T_mangoes
min_graph_T_mangoes_29 <- graph_values_29$min_graph_T_mangoes
max_graph_T_mangoes_29 <- graph_values_29$max_graph_T_mangoes
average_graph_T_Air_29 <- graph_values_29$average_graph_T_Air
min_graph_T_Air_29 <- graph_values_29$min_graph_T_Air
max_graph_T_Air_29 <- graph_values_29$max_graph_T_Air

average_graph_T_mangoes_30 <- graph_values_30$average_graph_T_mangoes
min_graph_T_mangoes_30 <- graph_values_30$min_graph_T_mangoes
max_graph_T_mangoes_30 <- graph_values_30$max_graph_T_mangoes
average_graph_T_Air_30 <- graph_values_30$average_graph_T_Air
min_graph_T_Air_30 <- graph_values_30$min_graph_T_Air
max_graph_T_Air_30 <- graph_values_30$max_graph_T_Air
average_graph_RH_Air_30 <- graph_values_30$average_graph_RH_Air
min_graph_RH_Air_30 <- graph_values_30$min_graph_RH_Air
max_graph_RH_Air_30 <- graph_values_30$max_graph_RH_Air

average_graph_T_mangoes_31 <- graph_values_31$average_graph_T_mangoes
min_graph_T_mangoes_31 <- graph_values_31$min_graph_T_mangoes
max_graph_T_mangoes_31 <- graph_values_31$max_graph_T_mangoes
average_graph_T_Air_31 <- graph_values_31$average_graph_T_Air
min_graph_T_Air_31 <- graph_values_31$min_graph_T_Air
max_graph_T_Air_31 <- graph_values_31$max_graph_T_Air



create_temp_hum_graphic_summary(box_1_1_1_graphic_summary, indices_files_1, 
                                average_graph_T_Air_1, min_graph_T_Air_1, max_graph_T_Air_1, 
                                average_graph_T_mangoes_1, min_graph_T_mangoes_1, max_graph_T_mangoes_1, 
                                average_graph_RH_Air_1, min_graph_RH_Air_1, max_graph_RH_Air_1)

create_temp_hum_graphic_summary(box_1_1_7_graphic_summary, indices_files_2, 
                                average_graph_T_Air_2, min_graph_T_Air_2, max_graph_T_Air_2, 
                                average_graph_T_mangoes_2, min_graph_T_mangoes_2, max_graph_T_mangoes_2, 
                                average_graph_RH_Air_2, min_graph_RH_Air_2, max_graph_RH_Air_2)

create_temp_hum_graphic_summary(box_1_1_12_graphic_summary, indices_files_3, 
                                average_graph_T_Air_3, min_graph_T_Air_3, max_graph_T_Air_3, 
                                average_graph_T_mangoes_3, min_graph_T_mangoes_3, max_graph_T_mangoes_3, 
                                average_graph_RH_Air_3, min_graph_RH_Air_3, max_graph_RH_Air_3)

create_temp_graphic_summary(box_1_3_1_graphic_summary, indices_files_4, 
                            average_graph_T_Air_4, min_graph_T_Air_4, max_graph_T_Air_4, 
                            average_graph_T_mangoes_4, min_graph_T_mangoes_4, max_graph_T_mangoes_4)

create_temp_graphic_summary(box_1_3_7_graphic_summary, indices_files_5, 
                            average_graph_T_Air_5, min_graph_T_Air_5, max_graph_T_Air_5, 
                            average_graph_T_mangoes_5, min_graph_T_mangoes_5, max_graph_T_mangoes_5)

create_temp_graphic_summary(box_1_3_12_graphic_summary, indices_files_6, 
                            average_graph_T_Air_6, min_graph_T_Air_6, max_graph_T_Air_6, 
                            average_graph_T_mangoes_6, min_graph_T_mangoes_6, max_graph_T_mangoes_6)

create_temp_hum_graphic_summary(box_1_4_1_graphic_summary, indices_files_7, 
                                average_graph_T_Air_7, min_graph_T_Air_7, max_graph_T_Air_7, 
                                average_graph_T_mangoes_7, min_graph_T_mangoes_7, max_graph_T_mangoes_7, 
                                average_graph_RH_Air_7, min_graph_RH_Air_7, max_graph_RH_Air_7)

create_temp_graphic_summary(box_1_4_7_graphic_summary, indices_files_8, 
                            average_graph_T_Air_8, min_graph_T_Air_8, max_graph_T_Air_8, 
                            average_graph_T_mangoes_8, min_graph_T_mangoes_8, max_graph_T_mangoes_8)

create_temp_graphic_summary(box_1_4_12_graphic_summary, indices_files_9, 
                            average_graph_T_Air_9, min_graph_T_Air_9, max_graph_T_Air_9, 
                            average_graph_T_mangoes_9, min_graph_T_mangoes_9, max_graph_T_mangoes_9)

create_temp_graphic_summary(box_2_1_1_graphic_summary, indices_files_10, 
                            average_graph_T_Air_10, min_graph_T_Air_10, max_graph_T_Air_10, 
                            average_graph_T_mangoes_10, min_graph_T_mangoes_10, max_graph_T_mangoes_10)

create_temp_graphic_summary(box_2_1_7_graphic_summary, indices_files_11, 
                            average_graph_T_Air_11, min_graph_T_Air_11, max_graph_T_Air_11, 
                            average_graph_T_mangoes_11, min_graph_T_mangoes_11, max_graph_T_mangoes_11)

create_temp_graphic_summary(box_2_1_12_graphic_summary, indices_files_12, 
                            average_graph_T_Air_12, min_graph_T_Air_12, max_graph_T_Air_12, 
                            average_graph_T_mangoes_12, min_graph_T_mangoes_12, max_graph_T_mangoes_12)

create_temp_hum_graphic_summary(box_2_2_1_graphic_summary, indices_files_13, 
                                average_graph_T_Air_13, min_graph_T_Air_13, max_graph_T_Air_13, 
                                average_graph_T_mangoes_13, min_graph_T_mangoes_13, max_graph_T_mangoes_13, 
                                average_graph_RH_Air_13, min_graph_RH_Air_13, max_graph_RH_Air_13)

create_temp_graphic_summary(box_2_2_3_graphic_summary, indices_files_14, 
                            average_graph_T_Air_14, min_graph_T_Air_14, max_graph_T_Air_14, 
                            average_graph_T_mangoes_14, min_graph_T_mangoes_14, max_graph_T_mangoes_14)

create_temp_hum_graphic_summary(box_2_2_6_graphic_summary, indices_files_15, 
                                average_graph_T_Air_15, min_graph_T_Air_15, max_graph_T_Air_15, 
                                average_graph_T_mangoes_15, min_graph_T_mangoes_15, max_graph_T_mangoes_15, 
                                average_graph_RH_Air_15, min_graph_RH_Air_15, max_graph_RH_Air_15)

create_temp_graphic_summary(box_2_2_10_graphic_summary, indices_files_16, 
                            average_graph_T_Air_16, min_graph_T_Air_16, max_graph_T_Air_16, 
                            average_graph_T_mangoes_16, min_graph_T_mangoes_16, max_graph_T_mangoes_16)

create_temp_hum_graphic_summary(box_2_2_12_graphic_summary, indices_files_17, 
                                average_graph_T_Air_17, min_graph_T_Air_17, max_graph_T_Air_17, 
                                average_graph_T_mangoes_17, min_graph_T_mangoes_17, max_graph_T_mangoes_17, 
                                average_graph_RH_Air_17, min_graph_RH_Air_17, max_graph_RH_Air_17)

create_temp_graphic_summary(box_2_4_1_graphic_summary, indices_files_18, 
                            average_graph_T_Air_18, min_graph_T_Air_18, max_graph_T_Air_18, 
                            average_graph_T_mangoes_18, min_graph_T_mangoes_18, max_graph_T_mangoes_18)

create_temp_graphic_summary(box_2_4_7_graphic_summary, indices_files_19, 
                            average_graph_T_Air_19, min_graph_T_Air_19, max_graph_T_Air_19, 
                            average_graph_T_mangoes_19, min_graph_T_mangoes_19, max_graph_T_mangoes_19)

create_temp_graphic_summary(box_3_1_12_graphic_summary, indices_files_20, 
                            average_graph_T_Air_20, min_graph_T_Air_20, max_graph_T_Air_20, 
                            average_graph_T_mangoes_20, min_graph_T_mangoes_20, max_graph_T_mangoes_20)

create_temp_graphic_summary(box_3_2_1_graphic_summary, indices_files_21, 
                            average_graph_T_Air_21, min_graph_T_Air_21, max_graph_T_Air_21, 
                            average_graph_T_mangoes_21, min_graph_T_mangoes_21, max_graph_T_mangoes_21)

create_temp_graphic_summary(box_3_2_3_graphic_summary, indices_files_22, 
                            average_graph_T_Air_22, min_graph_T_Air_22, max_graph_T_Air_22, 
                            average_graph_T_mangoes_22, min_graph_T_mangoes_22, max_graph_T_mangoes_22)

create_temp_graphic_summary(box_3_2_7_graphic_summary, indices_files_23, 
                            average_graph_T_Air_23, min_graph_T_Air_23, max_graph_T_Air_23, 
                            average_graph_T_mangoes_23, min_graph_T_mangoes_23, max_graph_T_mangoes_23)

create_temp_graphic_summary(box_3_2_10_graphic_summary, indices_files_24, 
                            average_graph_T_Air_24, min_graph_T_Air_24, max_graph_T_Air_24, 
                            average_graph_T_mangoes_24, min_graph_T_mangoes_24, max_graph_T_mangoes_24)

create_temp_graphic_summary(box_3_3_12_graphic_summary, indices_files_25, 
                            average_graph_T_Air_25, min_graph_T_Air_25, max_graph_T_Air_25, 
                            average_graph_T_mangoes_25, min_graph_T_mangoes_25, max_graph_T_mangoes_25)

create_temp_hum_graphic_summary(box_4_1_1_graphic_summary, indices_files_26, 
                                average_graph_T_Air_26, min_graph_T_Air_26, max_graph_T_Air_26, 
                                average_graph_T_mangoes_26, min_graph_T_mangoes_26, max_graph_T_mangoes_26, 
                                average_graph_RH_Air_26, min_graph_RH_Air_26, max_graph_RH_Air_26)

create_temp_graphic_summary(box_4_1_7_graphic_summary, indices_files_27, 
                            average_graph_T_Air_27, min_graph_T_Air_27, max_graph_T_Air_27, 
                            average_graph_T_mangoes_27, min_graph_T_mangoes_27, max_graph_T_mangoes_27)

create_temp_graphic_summary(box_4_2_1_graphic_summary, indices_files_28, 
                            average_graph_T_Air_28, min_graph_T_Air_28, max_graph_T_Air_28, 
                            average_graph_T_mangoes_28, min_graph_T_mangoes_28, max_graph_T_mangoes_28)

create_temp_graphic_summary(box_4_2_7_graphic_summary, indices_files_29, 
                            average_graph_T_Air_29, min_graph_T_Air_29, max_graph_T_Air_29, 
                            average_graph_T_mangoes_29, min_graph_T_mangoes_29, max_graph_T_mangoes_29)

create_temp_hum_graphic_summary(box_4_4_1_graphic_summary, indices_files_30, 
                                average_graph_T_Air_30, min_graph_T_Air_30, max_graph_T_Air_30, 
                                average_graph_T_mangoes_30, min_graph_T_mangoes_30, max_graph_T_mangoes_30, 
                                average_graph_RH_Air_30, min_graph_RH_Air_30, max_graph_RH_Air_30)

create_temp_graphic_summary(box_4_4_7_graphic_summary, indices_files_31, 
                            average_graph_T_Air_31, min_graph_T_Air_31, max_graph_T_Air_31, 
                            average_graph_T_mangoes_31, min_graph_T_mangoes_31, max_graph_T_mangoes_31)

##------End of Generating step Graphics----------
