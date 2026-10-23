
# ---------------------------------------------------------------------------------------
#
# Description       : The code provided is designed to generate a series of graphs and HTML information
#                     using the data in folder N°05 and to synthesise the statistical data into an document text
# 
# Authors           : PAVIET-SALOMON Yvanne <yvanne.paviet-salomon@inrae.fr>
# 
# Creation date     : 2024-06-16 22:39:55.294076
# Modification date : [1] "2024-09-08 10:00:23 CEST"
# fichier_info <- file.info("C:/01_R_data_paper_mangoes/00_script/05to06_script_color.R")
# date_modification <- fichier_info$mtime
# print(date_modification)
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

# source directory
path_src_color <- "../05_src_subset_dataset_C"

# result directory
path_res_color <- "../06_res_subset_dataset_C"

# Check if the directories exist
if (!dir.exists(path_src_color)) {
  stop("The source directory does not exist: ", path_src_color)
}
if (!dir.exists(path_res_color)) {
  stop("The result directory does not exist: ", path_res_color)
}

files <- list.files(path = path_src_color, pattern= "\\.txt$", full.names = TRUE)  #for .txt et .csv

maximal_value <- -Inf  
minimal_value <- Inf 

calculate_b_star_means <- function(file_path) {
  data <- read.table(file_path, header = TRUE, sep = "\t", stringsAsFactors = FALSE)
  
  # Filter columns starting with "b"
  b_cols <- grep("^b_D", names(data), value = TRUE)
  
  if (length(b_cols) > 0) {
    # Convert the relevant columns to numeric
    numeric_data <- as.data.frame(lapply(data[b_cols], as.numeric))
    
    # Calculate the means of the columns
    column_means <- colMeans(numeric_data, na.rm = TRUE)
    column_means <- round(column_means, 2)
  } else {
    column_means <- NULL
    cat("No b* columns found in file:", basename(file_path), "\n")
  }
  
  return(column_means)
}

# List to store the means results for each file
file_means <- list()

# Calculate the means of the b* columns for each file
for (file in files) {
  file_means[[file]] <- calculate_b_star_means(file)
  
  if (max(file_means[[file]], na.rm = TRUE) > maximal_value) {
    maximal_value <- max(file_means[[file]], na.rm = TRUE)
  }
  if (min(file_means[[file]], na.rm = TRUE) < minimal_value) {
    minimal_value <- min(file_means[[file]], na.rm = TRUE)
  }
}

# Transform the lists of means into data frames
mean_data_frames <- list()
for (file in names(file_means)) {
  means <- file_means[[file]]
  file_base_name <- basename(file)
  
  if (!is.null(means)) {
    # Create a data frame for the means of this file
    means_df <- data.frame(
      File = rep(file_base_name, length(means)),
      Column = names(means),
      Mean = means,
      stringsAsFactors = FALSE
    )
    
    # Add this data frame to the list
    mean_data_frames[[file]] <- means_df
  } else {
    cat("No b* data found for file:", file_base_name, "\n")
  }
}

# Combine all the data frames into one
combined_means_df <- do.call(rbind, mean_data_frames)

# Full path for the CSV and TXT files
csv_file_path <- file.path(path_res_color, "b_color_parameters_means.csv")
txt_file_path <- file.path(path_res_color, "b_color_parameters_means.txt")
colnames(combined_means_df) <- c("file_name", "b*_date", "b*_mean")

# Write the means to a CSV and TXT file
write.csv(combined_means_df, csv_file_path, row.names = FALSE)
write.table(combined_means_df, txt_file_path, sep = "\t", row.names = FALSE, quote = FALSE)

print("CSV and TXT files have been created successfully.")

# Generate HTML content
html_content <- "<html>
<head><title>Statistics Report</title></head>
<body>
<h1>Statistics Report</h1>"

# For each file, add the b* column means to the HTML content
for (file in files) {
  html_content <- paste0(html_content,
                         "<h2>", basename(file), "</h2>",
                         "<table border='1'>",
                         "<tr><th>b*</th><th>Mean</th></tr>")
  
  means <- file_means[[file]]
  if (!is.null(means)) {
    for (col in names(means)) {
      html_content <- paste0(html_content,
                             "<tr>",
                             "<td>", col, "</td>",
                             "<td>", round(means[col], 2), "</td>",
                             "</tr>")
    }
    
    # Generate and save the plot of the b_D* means
    b_cols <- grep("^b_D", names(means), value = TRUE)
    b_star_values <- means[b_cols]
    
    if (length(b_star_values) > 0) {
      png_filename <- file.path(path_res_color, paste0(basename(file), "_b_star_plot.png"))
      print(paste("Creating plot for file:", basename(file)))  # Debug message
      png(file = png_filename, width = 1200, height = 854, res = 150)
      
      file_name <- tools::file_path_sans_ext(basename(file))
      
      on.exit(dev.off(), add = TRUE)  # Ensure the device is turned off even in case of error
      

      
      # Generate the plot with the specified parameters
      par(mar = c(6, 4, 4, 3))

      # Add the date labels to the x-axis (adapted to your specific case)
      #axis(1, at = 1:length(b_cols), labels = gsub("^b_D", "", b_cols))
      date_axes <- c("4/18/2023 12:00",
                     "4/21/2023 12:00",
                     "4/24/2023 12:00",
                     "4/27/2023 12:00",
                     "4/30/2023 12:00",
                     "5/03/2023 12:00")
      
      file_info <- file.info(file)
      
      if (file_info$size > 12000 )
      {
        plot(b_star_values, type = "o", pch = 16,
             main =  paste(file_name, "\n Average of 20 mangoes\n 6 measure points for each mango"),
             xlab = "", ylab = "Average of b*", xaxt = "n", ylim = range (minimal_value, maximal_value))
      }
      if (file_info$size < 11000 & file_info$size > 6000)
      {
        plot(b_star_values, type = "o", pch = 16,
             main =  paste(file_name, "\n Average of 14 mangoes\n 6 measure points for each mango"),
             xlab = "", ylab = "Average of b*", xaxt = "n", ylim = range (minimal_value, maximal_value))
      }
      if (file_info$size < 3000 )
      {
        plot(b_star_values, type = "o", pch = 16,
             main =  paste(file_name, "\n Average of 3 mangoes\n 6 measure points for each mango"),
             xlab = "", ylab = "Average of b*", xaxt = "n", ylim = range (minimal_value, maximal_value))
      }
      if (file_info$size > 3000 & file_info$size < 6000 )
      {
        plot(b_star_values, type = "o", pch = 16,
             main =  paste(file_name, "\n Average of 6 mangoes\n 6 measure points for each mango"),
             xlab = "", ylab = "Average of b*", xaxt = "n", ylim = range (minimal_value, maximal_value))
      }
      axis(1, at = 1:length(b_cols), labels = date_axes, las = 2 , cex.axis = 0.7, cex.lab = 0.8)

      dev.off()
      
      html_content <- paste0(html_content, '<img src="', png_filename, '" alt="Means of b*">')
      print(paste("PNG file path:", png_filename))
      print(paste("Number of b* values:", length(b_star_values)))
    } else {
      print(paste("No b* values found for file:", basename(file)))  # Debug message
    }
    
    html_content <- paste0(html_content, "</table>")
  } else {
    html_content <- paste0(html_content, "<p>No b* data found for this file.</p>")
  }
}

# Close the body and HTML
html_content <- paste0(html_content, "</body></html>")

# Specify the path of the HTML file
html_path <- file.path(path_res_color, "statistic_color_mangoes.html")

# Write the HTML content to the specified file
write(html_content, file = html_path)

# Display the path to the generated HTML file
cat("HTML report generated: ", html_path, "\n")
