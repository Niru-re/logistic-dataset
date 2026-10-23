# ---------------------------------------------------------------------------------------
#
# Description       : The code provided is designed to generate a series of graphs
#                     using the data in folder N°03 and to synthesise the statistical data into an document text 
#                     
# 
# Authors           : PAVIET-SALOMON Yvanne <yvanne.paviet-salomon@inrae.fr>
# 
# Creation date     : 2024-06-16 15:08:19.697612
# Modification date : 2024-08-09
# Command specification for file modification date for traceability
# fichier_info <- file.info("C:/01_R_data_paper_mangoes/00_script/03to04_script_weight.R")
# date_modification <- fichier_info$mtime
# print(date_modification)
# Comments          : This script has specific graph generation functions and statistical analysis.
# 
# ---------------------------------------------------------------------------------------

# ----------------------------- path definition


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
path_src_weight <- "../03_src_subset_dataset_W"

# result directory
path_res_weight <- "../04_res_subset_dataset_W"

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
# to define the limit due to weigt of mangoes
maximal_value <- 0
minimal_value <- 1000

# List all text files in the folder
txt_files <- list.files(path = path_src_weight, pattern = "\\.txt$", full.names = TRUE)

# Initialize a list to store the loss percentages of each file
all_percentage_evolution <- list()

# Read each text file into a separate variable
for (file in txt_files) {
  # Get the file name without the extension and path
  file_name <- tools::file_path_sans_ext(basename(file))
  
  # Replace invalid characters with underscores to make the file name valid as a variable name
  valid_name <- make.names(file_name)
  
  # Read the text file
  data <- read.table(file, header = TRUE, sep = "\t", stringsAsFactors = FALSE)
  
  # Initialize a vector to store the loss percentages for the columns of this file
  percentage_evolution <- numeric(ncol(data) - 1)
  
  # Calculate the loss percentage for each column (except the first time column)
  for (i in 2:ncol(data)) {
    initial_value <- data[1, i]
    final_value <- data[nrow(data), i]
    if (initial_value != 0) {
      percentage_evolution[i - 1] <- ((initial_value - final_value) / initial_value) * 100
      if (initial_value > maximal_value) # initial ~ MAX - Experimental or max (data)
      {
        maximal_value <- max(initial_value)
      }
      if (final_value < minimal_value) # final ~ MIN - Experimental or min (data)
      {
        minimal_value <- min(final_value)
      }
    } else {
      percentage_evolution[i - 1] <- NA  # Avoid division by zero
    }
  }
  
  # Create a data frame with the file name and loss percentages
  percentage_evolution_df <- data.frame(Fichier = file_name, t(percentage_evolution))
  colnames(percentage_evolution_df)[-1] <- paste0("Column", 2:ncol(data))
  
  # Add the data frame to the list
  all_percentage_evolution[[file_name]] <- percentage_evolution_df
}

# Find the maximum number of columns (excluding the File column)
max_cols <- max(sapply(all_percentage_evolution, ncol))

# Align the columns of each data frame by adding missing columns with NA
all_percentage_evolution <- lapply(all_percentage_evolution, function(df) {
  if (ncol(df) < max_cols) {
    new_cols <- setdiff(paste0("Column", 2:max_cols), colnames(df)[-1])
    df[new_cols] <- NA
  }
  return(df)
})

# Combine all the data frames into one
combined_df <- do.call(rbind, all_percentage_evolution)

# Specify the output path
output_path <- file.path(path_res_weight, "percentage_evolution.txt")

# Write the loss percentages to a text file
write.table(combined_df, file = output_path, sep = "\t", col.names = TRUE, row.names = FALSE, quote = FALSE)

# Display a confirmation message
cat("The file has been successfully created at:", output_path, "\n")



files <- list.files(path = path_src_weight, pattern = "\\.txt$", full.names = TRUE)

process_file <- function(file) {
  # Read data from the file
  data <- read.table(file, header = TRUE, sep = "\t", stringsAsFactors = FALSE)
  
  # Convert Time to POSIXct class
  data$Time <- as.POSIXct(data$Time, format = "%d/%m/%Y %H:%M")
  
  # Create a list to store the plots
  plots <- list()
  
  # Loop over each column starting from the second
  for (i in 2:ncol(data)) {

    column_name <- colnames(data)[i]
    
    # Extract the box position and mango number
    parts <- strsplit(column_name, "_|\\.")[[1]]
    box_position <- paste(parts[2], parts[3], parts[4], sep = "_")
    mango_number <- parts[5]
    
    # Extract the values from the column
    values <- data[, i]
    
    # Calculate the loss percentage
    initial_value <- values[1]
    final_value <- values[length(values)]
    percentage_loss <- ((initial_value - final_value) / initial_value) * 100
    
    # Graphic file name
    graphic_file <- file.path(path_res_weight, paste0(column_name, ".png"))
    
    # Open the PNG file for the plot
    png(file = graphic_file, width = 1200, height = 854, res = 150)
    
    #base_name <- tools::file_path_sans_ext(basename(graphic_file))

    # Generate the plot
    par(mar = c(8, 4, 4, 3)) 
    
    plot(data$Time, values,
         type = "o", pch = 16, col = "black",
         xlab ="",
         ylab = "mass(g)",
         main = paste("Mangoes mass evolution \nBox position:", box_position, "\n Mango number:", mango_number),
         #ylim = range(data[, i], na.rm = TRUE),  # Optional
         ylim = range (minimal_value, maximal_value, na.rm = TRUE), # to fix y_limits to each graph
         xlim = range(data$Time, na.rm = TRUE),  
         xaxt = "n")  
    
    # Add x-axis labels with formatted dates
    axis.POSIXct(1, at = seq(min(data$Time), max(data$Time), by = "day"),
                 format = "%m/%d/%Y %H:%M", las = 2)  # las = 2 vertical date
    
    # Add the legend with the loss percentage
    legend("topright", legend = paste("Percentage loss over 15 days:", round(percentage_loss, 2), "%"), bty = "n")
    
    # Store the plot in the list
    plots[[i - 1]] <- recordPlot()
    
    # Close the output PNG file
    dev.off()
    Sys.sleep(0.1)  # 0,1s Freeze to avoid lag
    
  }
  
  # Return the list of plots
  return(plots)
}

# Apply the function to each file and obtain the plots
all_plots <- lapply(files, process_file)