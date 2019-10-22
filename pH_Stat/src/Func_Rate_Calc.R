# Load all files in folder ----------------

LoadAll <- function(path){
  
  # Find all files in folder
  files <- unlist(list.files(path = path, pattern = "*.csv", full.names = TRUE))
  file_names <- unlist(list.files(path = path, pattern =  "*.csv"))
  
  # Load data with lapply
  data <- lapply(files, function(x){
    readr::read_csv(x)
  }
  )
  # Rename list items
  names(data) <- str_replace(file_names, pattern = ".csv", replacement = "")
  
  return(data)
  
}

##############################################
##Load all pH stat files from within a  folder
##############################################
CalcStat <- function(path){
  
  my_files <- unlist(list.files(path = path, 
                                pattern = "*.csv", full.names = TRUE))
  file_names <- unlist(list.files(path = path,
                                  pattern = "*.csv"))

  
  # Adjust raw data
  
  raw_data <- lapply(my_files, function(x){
    readr::read_csv(x)
  }
  )
  
  names(raw_data) <- str_replace(file_names, pattern = ".csv", replacement = "")
  

  # Adjust raw data

  raw_data <- lapply(raw_data, function(x)
    x <-
      x %>%
      # na.omit() %>%
      mutate(
        Time_h = Time_s / 3600,
        TitrantConc_mol = mean(c((first((Mass_of_Na2CO3_in_titrant_g * 20) / 105.99)), (first((Mass_of_CaCl2_in_titrant_g * 20) / 147.02)))),
        Vol_titr_added = Volume_mL - first(Volume_mL),
        Duration = Time_h - first(Time_h),
        Rate = ((Vol_titr_added/1000) * TitrantConc_mol)/((SpecificSA * Mass_of_Seed_g) * Duration),
        log_Rate_mol_m2_h = log10(Rate),
        mmoles_added = TitrantConc_mol * (Vol_titr_added / 1000) * 1000,
        NaHCO3_mmolL = (Mass_of_NaHCO3_g / 84.01) * 1000 * 2,
        deviation = Setpoint_pH - pH
      ))
  

  # Create list "trim_data" this stores all experiments as individual dataframes in a list

  trim_data <- lapply(raw_data, function(x)
    x <-
      x %>%
      # na.omit() %>%
      filter(Time_s > 3600 * 4) %>%
      mutate(
        Time_h = Time_s / 3600,
        TitrantConc_mol = mean(c((first((Mass_of_Na2CO3_in_titrant_g * 20) / 105.99)), (first((Mass_of_CaCl2_in_titrant_g * 20) / 147.02)))),
        Vol_titr_added = Volume_mL - first(Volume_mL),
        Duration = Time_h - first(Time_h),
        Rate = ((Vol_titr_added/1000) * TitrantConc_mol)/((SpecificSA * Mass_of_Seed_g) * Duration),
        log_Rate_mol_m2_h = log10(Rate),
        mmoles_added = TitrantConc_mol * (Vol_titr_added / 1000) * 1000,
        NaHCO3_mmolL = (Mass_of_NaHCO3_g / 84.01) * 1000 * 2,
        deviation = Setpoint_pH - pH
      ))
  

  # Create dataframe "data" this combines all the individual dataframes in trim_data into one dataframe

 rate_data<- lapply(trim_data, function(x)
    x <-
      x %>%
      summarise(
        Key = last(Key),
        Date = last(Date),
        Mass_of_Seed_g = last(Mass_of_Seed_g),
        NaHCO3_g = last(Mass_of_NaHCO3_g),
        NaHCO3_mmolL = last(NaHCO3_mmolL),
        TitrantConc_mmol = last(TitrantConc_mol*1000),
        Expt_Duration = last(Duration),
        Titr_Volume = last(Vol_titr_added),
        Designation = last(Designation),
        Temp_C_mean = mean(Temp_C),
        Temp_C_sd = sd(Temp_C),
        pH_mean = mean(pH),
        pH_sd = sd(pH),
        pH_Setpoint = last(Setpoint_pH),
        mMoles_ppt = (last(TitrantConc_mol) * (Titr_Volume / 1000)) * 1000,
        Rate = last(Rate),
        log_Rate_mol_m2_h = log10(Rate)
      ))
  rate_data<- dplyr::bind_rows(rate_data)
  
  
  return(list(raw_data = raw_data,
              trim_data = trim_data,
              trim_data = trim_data,
             rate_data= rate_data))
  
}

###########################################
## Plotting raw data
######################################
    
 tri_plot <- function(data, savepath){
   lapply(data, function(x) {
      plot1 <- ggplot(data = x) +
        geom_line(aes(x = Time_h, y = pH), color = "#009E73") +
        geom_line(aes(x = Time_h, y = Setpoint_pH), color = "grey", linetype = "dashed") +
        geom_line(aes(x = Time_h, y = Setpoint_pH + 0.005), color = "grey", linetype = "dotted") +
        geom_line(aes(x = Time_h, y = Setpoint_pH - 0.005), color = "grey", linetype = "dotted") +
        theme_bw() +
        theme(plot.title = element_text(size = 10)) +
        labs(x = "Time (h)", y = "pH", title = paste(x[["Date"]][1], "-", x[["Designation"]][1]))
      
      plot2 <- ggplot(data = x) +
        geom_line(aes(x = Time_h, y = Vol_titr_added), color = "#efd400") +
        theme_bw() +
        ylim(0, 15.5)+
        labs(x = "Time (h)", y = bquote("Volume (mL)"))
      
      plot3 <- ggplot(data = x) +
        geom_line(aes(x = Time_h, y = log_Rate_mol_m2_h), color = "#a41790") +
        geom_hline(yintercept = last(x$log_Rate_mol_m2_h), linetype="dashed")+
        theme_bw() +
        ylim(-6.5, -3.8)+
        labs(x = "Time (h)", y = expression(paste("Log Rate" ~ "(mol", ~ "m"^{
          -2
        }, ~ "h"^{
          "-1"
        }, ")")))
      
      grid <- plot_grid(plot1, plot2, plot3, nrow = 3, align = "vh")
      
      grid <- add_sub(grid,
                      paste(
                        " Key = ", x[["Key"]][1], "\n",
                        "[NaHCO3] mmolL = ", round(x[["NaHCO3_mmolL"]][1], digits = 2), "\n",
                        "log Rate =", round(x[["log_Rate_mol_m2_h"]][nrow(x)], digits = 2), "mol m2 h-1", "\n",
                        "Calcite precipitated =", round(x[["mmoles_added"]][nrow(x)], digits = 4), "millimoles", "\n",
                        "Titrant Conc =", round(x[["TitrantConc_mol"]], digits = 3)*1000, "mM"
                      ),
                      x = 0.05, hjust = 0, size = 10
      )
      ggsave(filename = paste0(x[["Key"]][1],  ".png", sep = ""), grid, path = savepath, height = 15, width = 10, dpi = 350, units = "cm", type = "cairo")
})}

###########################################
##Colour Scale
###########################################

# Blue <- "#56B4E9"
# Yellow <- "#efd400"
# Purple <- "#a41790"
# Grey <- "#9fa0a0"
# Green <-  "#009E73"
# Orange <- "#D55E00"
# Pink <- "#CC79A7"
# Red <- "#e9566b"

DH_Cols <- c("#009E73", "#efd400",  "#a41790",  "#9fa0a0",  "#D55E00", "#56B4E9",  "#CC79A7",  "#e9566b",  "#0072B2")
