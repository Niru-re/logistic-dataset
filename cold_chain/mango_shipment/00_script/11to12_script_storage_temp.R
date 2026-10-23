
# ---------------------------------------------------------------------------------------
#
# Description       : 
# 
# Authors           : PAVIET-SALOMON Yvanne <yvanne.paviet-salomon@inrae.fr>
# 
# Creation date     : 2024-06-18 20:14:31.006795
# Modification date : 2024-08-04
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
path_src_cold_room_temp <- "../11_src_subset_dataset_SR"

# -------------- results

# result directory
path_res_cold_room_temp <- "../12_res_subset_dataset_SR"

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

# Load the data
file <- file.path(path_src_cold_room_temp, "Storage_Room_Temp_Hum.txt")
data <- read.table(file, header = TRUE, sep = "\t")
base_name <- tools::file_path_sans_ext(basename(file))

# Convert the Time column to a POSIXct object
data$Time <- as.POSIXct(data$Time, format = "%d/%m/%Y %H:%M")

# Define the limits for the Y axes
temp_limits <- range(c(data$T_16C, data$T_21C), na.rm = TRUE)
relative_humidity_limits <- range(c(data$H_16C, data$H_21C), na.rm = TRUE)

# Generate the plot for temperatures
par(mar = c(5, 4, 4, 5) + 0.1)  # Adjust the margins
plot(data$Time, data$T_16C, type = "l", main = paste("Storage Room \n", base_name),
     lwd = 2,
     xlab = "", ylab = "Temperature (°C)", col = "green", ylim = temp_limits)
lines(data$Time, data$T_21C, col = "red", lwd = 2)

# Add the humidity curves on axis 4
par(new = TRUE)
plot(data$Time, data$H_16C, type = "l", col = "blue", ylim = relative_humidity_limits,
     axes = FALSE, xlab = "", ylab = "", lwd = 2)
lines(data$Time, data$H_21C, col = "black", lwd = 2)
axis(4, at = pretty(relative_humidity_limits), col = "blue", col.axis = "blue", las = 1)
mtext("Relative Humidity (%)", side = 4, line = 3, col = "blue")
par(xpd = TRUE)
# Add a legend below the plot
legend("bottom", inset = c(0, -0.2), legend = c("T_16C", "T_21C", "H_16C", "H_21C"), 
       col = c("green", "red", "blue", "black"), lty = 1, bty = "n", horiz = TRUE, cex = 0.8, lwd = 2)

# If you want to save the plot to a PNG file
png_filename <- file.path(path_res_cold_room_temp, paste0(base_name, ".png"))
png(png_filename, width = 1200, height = 854, res = 150)

# Generate the plot for temperatures
par(mar = c(5, 4, 4, 5) + 0.1)  # Adjust the margins
plot(data$Time, data$T_16C, type = "l", main = paste("Storage Room \n", base_name),
     xlab = "", ylab = "Temperature (°C)", col = "green", ylim = temp_limits, lwd = 2)
lines(data$Time, data$T_21C, col = "red", lwd = 2)

# Add the humidity curves on axis 4
par(new = TRUE)
plot(data$Time, data$H_16C, type = "l", col = "blue", ylim = relative_humidity_limits, axes = FALSE,
     xlab = "", ylab = "", lwd = 2)
lines(data$Time, data$H_21C, col = "black", lwd = 2)
axis(4, at = pretty(relative_humidity_limits), col = "blue", col.axis = "blue", las = 1)
mtext("Relative Humidity (%)", side = 4, line = 3, col = "blue")
par(xpd = TRUE)
# Add a legend below the plot
legend("bottom", inset = c(0, -0.2), legend = c("T_16C", "T_21C", "H_16C", "H_21C"), 
       col = c("green", "red", "blue", "black"), lty = 1, bty = "n", horiz = TRUE, cex = 0.8, lwd = 2)

# Close the PNG file
dev.off()

# Calculate the column means
mean_T_16C <- round(mean(data$T_16C, na.rm = TRUE), 2)
mean_T_21C <- round(mean(data$T_21C, na.rm = TRUE), 2)
mean_H_16C <- round(mean(data$H_16C, na.rm = TRUE), 2)
mean_H_21C <- round(mean(data$H_21C, na.rm = TRUE), 2)

# Create a data frame for the means
mean_data <- data.frame(
  Column = c("T_16C", "T_21C", "H_16C", "H_21C"),
  Mean = c(mean_T_16C, mean_T_21C, mean_H_16C, mean_H_21C)
)

# Write the means to a text file
txt_filename <- file.path(path_res_cold_room_temp, "Average_Storage_Room_Temp_Hum.txt")
write.table(mean_data, file = txt_filename, row.names = FALSE, quote = FALSE, sep = "\t")

# Write the means to a CSV file
csv_filename <- file.path(path_res_cold_room_temp, "Average_Storage_Room_Temp_Hum.csv")
write.csv(mean_data, file = csv_filename, row.names = FALSE)
