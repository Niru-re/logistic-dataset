
# ---------------------------------------------------------------------------------------
#
# Description       : 
# 
# Authors           : PAVIET-SALOMON Yvanne <yvanne.paviet-salomon@inrae.fr>
# 
# Creation date     : 2024-06-18 22:50:59.840087
# Modification date : 2024-06-18
# 
# Comments          : 
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


# -------------- sources

# source directory
path_src_ph <- "../07_src_subset_dataset_PH"

# -------------- results

# result directory
path_res_ph <- "../08_res_subset_dataset_PH"


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

# List all text files in the folder
txt_files <- list.files(path = path_src_ph, pattern = "\\.txt$", full.names = TRUE)

# Initialize a list to store the percentages of each file
all_percentage_evolution <- list()

maximal_value <- -Inf  
minimal_value <- Inf  

# Read each text file into a separate variable
for (file in txt_files) {
  # Get the file name without the extension and path
  file_name <- tools::file_path_sans_ext(basename(file))
  
  # Replace invalid characters with underscores to make the file name valid as a variable name
  valid_name <- make.names(file_name)
  
  # Read the text file
  data <- read.table(file, header = TRUE, sep = "\t", stringsAsFactors = FALSE)
  
  # Initialize a vector to store the percentages for the columns of this file
  percentage_evolution <- numeric(ncol(data) - 1)
  
  
  # Calculate the percentage for each column (except the first time column)
  for (i in 2:ncol(data)) {
    initial_value <- data[1, i]
    final_value <- data[nrow(data), i]
    
    # Update maximal_value and minimal_value with all values in the column
    column_values <- data[, i]
    if (max(column_values, na.rm = TRUE) > maximal_value) {
      maximal_value <- max(column_values, na.rm = TRUE)
    }
    if (min(column_values, na.rm = TRUE) < minimal_value) {
      minimal_value <- min(column_values, na.rm = TRUE)
    }
    
    if (initial_value != 0) {
      percentage_evolution[i - 1] <- ((final_value - initial_value ) / initial_value) * 100
    } else {
      percentage_evolution[i - 1] <- NA  # Avoid division by zero
    }
    # Print the results
    print("Percentage Evolution:")
    print(percentage_evolution)
    print(paste("Maximal Value:", maximal_value))
    print(paste("Minimal Value:", minimal_value))
  }
  
  # Create a data frame with the file name and pencentage evolution
  percentage_evolution_df <- data.frame(Fichier = file_name, t(percentage_evolution))
  colnames(percentage_evolution_df)[-1] <- paste0("PH_mangoes_Column", 2:ncol(data))
  
  # Add the data frame to the list
  all_percentage_evolution[[file_name]] <- percentage_evolution_df
}

# Find the maximum number of columns (excluding the File column)
max_cols <- max(sapply(all_percentage_evolution, ncol))

# Align the columns of each data frame by adding missing columns with NA
all_percentage_evolution <- lapply(all_percentage_evolution, function(df) {
  if (ncol(df) < max_cols) {
    new_cols <- setdiff(paste0("PH_mangoes_Column", 2:max_cols), colnames(df)[-1])
    df[new_cols] <- NA
  }
  return(df)
})

# Combine all the data frames into one
combined_df <- do.call(rbind, all_percentage_evolution)

# Specify the output path
output_path <- file.path(path_res_ph, "percentage_PH_evolution.txt")

# Write the percentages to a text file
write.table(combined_df, file = output_path, sep = "\t", col.names = TRUE, row.names = FALSE, quote = FALSE)

# Display a confirmation message
cat("The file has been successfully created at:", output_path, "\n")

#-------------------------Graphics

files <- list.files(path = path_src_ph, pattern = "\\.txt$", full.names = TRUE)

process_file <- function(file) {
  # Read data from the file
  data <- read.table(file, header = TRUE, sep = "\t", stringsAsFactors = FALSE)
  
  # Convert Time to POSIXct class
  data$Time <- as.POSIXct(data$Time, format = "%d/%m/%Y %H:%M")
  
  # Create a list to store the plots (if you need specific use)
  plots <- list()
  
  
  #Loop over each column starting from the second
  for (i in 2:ncol(data)) {
    
    column_name <- colnames(data)[i]
    
    # Extract the box position and mango number
    parts <- strsplit(column_name, "_|\\.")[[1]]
    box_position <- paste(parts[2], parts[3], parts[4], sep = "_")
    mango_number <- parts[5]
    
    # Extract the values from the column
    values <- data[, i]
    
    # Graphic file name
    graphic_file <- file.path(path_res_ph, paste0(column_name, ".png"))
    
    # Open the PNG file for the plot
    png(file = graphic_file, width = 1200, height = 854, res = 150)
    
    #base_name <- tools::file_path_sans_ext(basename(graphic_file))
    
    # Generate the plot
    par(mar = c(8, 4, 4, 3)) 
    
    plot(data$Time, values,
         type = "o", pch = 17, col = "red",
         xlab ="",
         ylab = "PH",
         main = paste("Mangoes PH evolution \nBox position:", box_position, "\n Mango number:", mango_number),
         #ylim = range(data[, i], na.rm = TRUE), 
         ylim = range (minimal_value, maximal_value), # to fix y_limits to each graph
         xlim = range(data$Time, na.rm = TRUE), 
         xaxt = "n")  
    # Add x-axis labels with formatted dates
    axis.POSIXct(1, at = seq(min(data$Time), max(data$Time), by = "day"),
                 format = "%m/%d/%Y %H:%M", las = 2)

    # Store the plot in the list
    plots[[i - 1]] <- recordPlot()
    
    # close the output png file
    dev.off()
    Sys.sleep(0.1)  
    
  }
  
  # return the list of the plots
  return(plots)
}

# Apply the function to each file and obtain the plots
all_plots <- lapply(files, process_file)

