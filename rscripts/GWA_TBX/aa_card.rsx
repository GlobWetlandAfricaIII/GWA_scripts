#' Map agreement
#'
#' @title aa_card
#' @description Calculates Agreement and Area of disproportioned sampling
#' @param data confusion matrix or cbind(reference,map)
#' @param w stratum weights
#' @param A total area (optional)
#' @param confusion_matrix define if data contains a confusion matrix or sample vectors
#' @return list of accuracy and area proportion estimates and associated standard errors
#' @references Card, D.H. (1982). Using Known Map Category Marginal Frequencies to Improve Estimates of Thematic Map Accuracy. Photogrammetric Engineering and Remote Sensing, 48, 431-439 
#' @examples   
#' m <- matrix(c(410,67,26,369), nrow=2)
#' A <- c(828837,33067283)
#' w_j <- A/sum(A)
#' aa_card(m, w_j)
#' @author Dirk Pflugmacher
#' 

aa_card <- function(data, w=NULL, area=NULL, confusion_matrix=T) {
  
  
  # data   : confusion matrix with rows = map; columns = reference
  #       where the elements represent sampling counts
  # w   : stratum weights
  # i   : subscript i refers to reference class
  # j   : subscript j refers to map class
  
  
  if (missing(data)) {
    message("result <- aa_card(n, w=NULL, area=NULL, confusion_matrix=T)")
    return(invisible(NULL))
  }
  
  if (confusion_matrix==F) {
    reference <- data[,1]
    map <- data[,2] 
    
    if (class(data[,1])=='factor') lvl=levels(data[,1]) else lvl=NULL
    
    reference  <- as.character(reference)
    map <- as.character(map)
    
    if (is.null(lvl)) lvl <- unique(c(map,reference))
    lvl <- sort(lvl)
    
    reference <- factor(reference, levels=lvl)
    map <- factor(map, levels=lvl)
    
    n <- table(map, reference)
    
    
  } else n <- data
  
  
  
  class <- colnames(n)
  if (length(class)==0) class <- 1:nrow(n)
  
  
  if (class(n)=='table') n <- as.matrix(unclass(n))
  
  # map totals
  n_j <- apply(n,1,sum)
  n_j_m <- matrix(n_j, nrow(n), nrow(n), byrow=F)
  
  # refrence totals matrix
  n_i <- apply(n,2,sum)
  n_i_m <- matrix(n_i, nrow(n), nrow(n), byrow=F)
  
  # stratum weights
  if (is.null(w)) {
    w_j <- n_j/sum(n)
  } else w_j <- w
  
  # proportional error matrix
  p <- n * matrix(w_j/n_j, nrow=nrow(n), ncol=nrow(n))
  colnames(p) <- class
  rownames(p) <- class  
  class <- as.numeric(class)
  
  # User's Accuracy
  ua <- diag(p)/apply(p,1,sum)
  pa <- diag(p)/apply(p,2,sum)
  
  
  # Overall Accuracy
  oa = sum(diag(p))
  
  # area proportion
  p_i = apply(p,2,sum)
  
  
  # weight matrix
  w_j_m <- matrix(w_j, nrow(n), nrow(n), byrow=F)
  
  # standard error of reference class proportions according to Card
  p_i_se <- sqrt(apply(p * (w_j_m-p)/n_j_m ,2,sum))
  
  # standard error of comission error
  # simple random sampling
  #   term1 <- diag(p)*p_i^-4
  #   term2 <-  p * (w_j_m-p)/(w_j_m *sum(n)) 
  #   diag(term2) <- 0
  #   term2 <- diag(p) * apply(term2, 2, sum)
  #   term3 <- term2 + (w_j- diag(p)) * ( p_i - diag(p))^2   / (w_j*sum(n))
  #   se_pa2 <- term1 * term3
  #   sqrt(se_pa2)
  
  # standard error of producer's accurarcy
  # stratified sampling
  term1 <- diag(p) * (p_i)^(-4)
  term2 <-  p * (w_j_m-p)/n_j_m 
  diag(term2) <- 0
  term2 <- diag(p) * apply(term2, 2, sum)
  term3 <- (w_j- diag(p)) * ( p_i - diag(p))^2/ n_j
  pa_se <- sqrt(term1 * (term2+term3))
  # format(round(pa_se, digits=5), scientific=F)
  
  
  # standard error of user's accuracy
  ua_se <- diag(p) * (w_j- diag(p)) / (n_j * w_j^2)
  ua_se <- sqrt(ua_se)  
  # format(round(ua_se, digits=5), scientific=F)
  
  # standard error of overall accuracy
  oa_se <- sum(diag(p) * (w_j- diag(p)) / n_j)
  
  
  # standard error of reference class proportions according to Olofsson
  p_i_se0 <- w_j_m^2 * (n/n_j) * (1-(n/n_j)) / (n_j-1)
  p_i_se0  <- (sqrt(apply(p_i_se0, 2, sum)))
  
  df <- data.frame(cbind(class,ua, pa, p_i, p_i_se, ua_se, pa_se))
  df$w <- w_j
  
  da <- data.frame(class=df$class)
  da$proportion <- df$p_i
  da$proportion_ci  <- 1.96 * df$p_i_se
  
  if (!is.null(area)) {  
    da$area <- area*da$proportion
    da$area_ci  <- area * 1.96 * df$p_i_se
  }
  
  return(list(cm=n, cmp=p, stats=df, accuracy=c(oa,oa_se), area=da))
  
}