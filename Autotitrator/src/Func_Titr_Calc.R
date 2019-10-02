

#Read all file in directory
load.Titr.csv <- function(Series){
  
  Series_path <- here::here(paste0("/Autotitrator/Data/Filtered/",Series)) #This combines the folder and path
  
  files = list.files(path = Series_path, pattern="*.csv", full.names = TRUE) #Lists full file paths for all files in the destination folder
  file_names <- unlist(list.files(path = Series_path,
                                  pattern = "*.csv"))
  column_classes <- c("character", "numeric", "numeric")
  
  Raw_Alk <- lapply(files, function(x) {
    readr::read_csv(x, col_types = cols(
      Date = col_character(),
      Time_s = col_double(),
      Temp_C = col_double(),
      pH = col_double(),
      pH_mV = col_double(),
      Rate_mL_h = col_double(),
      Volume_mL = col_double(),
      Sample_mass_g = col_double(),
      Key = col_character(),
      Normality = col_double()
    ))
  })
  
  names(Raw_Alk) <- str_replace(file_names, pattern = ".csv", replacement = "")
  
  ##############################################
  ## Adjust raw data
  ##############################################    
  calc_data <- lapply(Raw_Alk, function(x)
    x <-
      x %>%
      na.omit %>%
      mutate(
        Time_h = Time_s / 3600,
        F1 = (Sample_mass_g + Volume_mL)*(10^-pH)
      ))
return(bind_rows(calc_data))
}



#Creates a function called Alk.Calc which takes a dataframe and computes alkalinity via the gram function method https://water.usgs.gov/owq/FieldManual/Chapter6/section6.6/html/section6.6.4.htm
AlkCalc <- function(Data){
  Data%>%
    group_by(Key, Sample_mass_g, Normality) %>%
    do(model = lm(Volume_mL ~ F1, data = filter(.,pH < 3.6))) %>% #filter(.,F1 > max(F1)-0.015)
    rowwise() %>%
    tidy(model) %>%
    select(Key, term, estimate) %>%
    filter(term == "(Intercept)") %>%
    mutate(Alk_meq_L = 1000 * estimate * Normality / Sample_mass_g)}

#Colour scheme
DH_Cols <- c("#009E73", "#efd400",  "#a41790",  "#9fa0a0",  "#D55E00", "#56B4E9",  "#CC79A7",  "#e9566b",  "#0072B2")

theme_dh <- function (base_size = 12, base_family = "") 
{
  theme_grey(base_size = base_size, base_family = base_family) %+replace% 
    theme(axis.text = element_text(size = rel(0.8)),
          #axis.title = element_text(face = "bold"), 
          axis.ticks = element_line(colour = "black"),
          aspect.ratio = 1,
          legend.key = element_rect(colour = "grey80"), 
          panel.background = element_rect(fill = "white", colour = NA), 
          panel.border = element_rect(fill = NA, colour = "grey50"), 
          panel.grid.major = element_line(colour = "grey80", size = 0.2, linetype = "dashed"), 
          panel.grid.minor = element_line(colour = "grey80", size = 0.5, linetype = "dashed"), 
          strip.background = element_rect(fill = "grey80", colour = "grey50", 
                                          size = 0.2))
}