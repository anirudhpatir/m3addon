// Generated by using Rcpp::compileAttributes() -> do not edit by hand
// Generator token: 10BE3573-1514-4C36-9D1C-5A225CD40393

#include <RcppArmadillo.h>
#include <Rcpp.h>

using namespace Rcpp;

// sp_show_storage
Rcpp::NumericMatrix sp_show_storage(const arma::sp_mat& x);
RcppExport SEXP _m3addon_sp_show_storage(SEXP xSEXP) {
BEGIN_RCPP
    Rcpp::RObject rcpp_result_gen;
    Rcpp::RNGScope rcpp_rngScope_gen;
    Rcpp::traits::input_parameter< const arma::sp_mat& >::type x(xSEXP);
    rcpp_result_gen = Rcpp::wrap(sp_show_storage(x));
    return rcpp_result_gen;
END_RCPP
}
// subsetSM
arma::sp_mat subsetSM(const arma::sp_mat& a, Rcpp::NumericVector rind, Rcpp::NumericVector cind);
RcppExport SEXP _m3addon_subsetSM(SEXP aSEXP, SEXP rindSEXP, SEXP cindSEXP) {
BEGIN_RCPP
    Rcpp::RObject rcpp_result_gen;
    Rcpp::RNGScope rcpp_rngScope_gen;
    Rcpp::traits::input_parameter< const arma::sp_mat& >::type a(aSEXP);
    Rcpp::traits::input_parameter< Rcpp::NumericVector >::type rind(rindSEXP);
    Rcpp::traits::input_parameter< Rcpp::NumericVector >::type cind(cindSEXP);
    rcpp_result_gen = Rcpp::wrap(subsetSM(a, rind, cind));
    return rcpp_result_gen;
END_RCPP
}
// calculateScoresCPP
arma::vec calculateScoresCPP(const arma::sp_mat& a, const Rcpp::NumericVector Rgenevec);
RcppExport SEXP _m3addon_calculateScoresCPP(SEXP aSEXP, SEXP RgenevecSEXP) {
BEGIN_RCPP
    Rcpp::RObject rcpp_result_gen;
    Rcpp::RNGScope rcpp_rngScope_gen;
    Rcpp::traits::input_parameter< const arma::sp_mat& >::type a(aSEXP);
    Rcpp::traits::input_parameter< const Rcpp::NumericVector >::type Rgenevec(RgenevecSEXP);
    rcpp_result_gen = Rcpp::wrap(calculateScoresCPP(a, Rgenevec));
    return rcpp_result_gen;
END_RCPP
}
// logNormCPP
arma::sp_mat logNormCPP(const arma::sp_mat& a);
RcppExport SEXP _m3addon_logNormCPP(SEXP aSEXP) {
BEGIN_RCPP
    Rcpp::RObject rcpp_result_gen;
    Rcpp::RNGScope rcpp_rngScope_gen;
    Rcpp::traits::input_parameter< const arma::sp_mat& >::type a(aSEXP);
    rcpp_result_gen = Rcpp::wrap(logNormCPP(a));
    return rcpp_result_gen;
END_RCPP
}
// colStdDev
arma::mat colStdDev(arma::sp_mat& a);
RcppExport SEXP _m3addon_colStdDev(SEXP aSEXP) {
BEGIN_RCPP
    Rcpp::RObject rcpp_result_gen;
    Rcpp::RNGScope rcpp_rngScope_gen;
    Rcpp::traits::input_parameter< arma::sp_mat& >::type a(aSEXP);
    rcpp_result_gen = Rcpp::wrap(colStdDev(a));
    return rcpp_result_gen;
END_RCPP
}
// rowStdDev
arma::mat rowStdDev(arma::sp_mat& a);
RcppExport SEXP _m3addon_rowStdDev(SEXP aSEXP) {
BEGIN_RCPP
    Rcpp::RObject rcpp_result_gen;
    Rcpp::RNGScope rcpp_rngScope_gen;
    Rcpp::traits::input_parameter< arma::sp_mat& >::type a(aSEXP);
    rcpp_result_gen = Rcpp::wrap(rowStdDev(a));
    return rcpp_result_gen;
END_RCPP
}
// vstExprsCPP
arma::mat vstExprsCPP(const arma::sp_mat& a, const double eP, const double aD, bool return_sparse, bool calc_zeros);
RcppExport SEXP _m3addon_vstExprsCPP(SEXP aSEXP, SEXP ePSEXP, SEXP aDSEXP, SEXP return_sparseSEXP, SEXP calc_zerosSEXP) {
BEGIN_RCPP
    Rcpp::RObject rcpp_result_gen;
    Rcpp::RNGScope rcpp_rngScope_gen;
    Rcpp::traits::input_parameter< const arma::sp_mat& >::type a(aSEXP);
    Rcpp::traits::input_parameter< const double >::type eP(ePSEXP);
    Rcpp::traits::input_parameter< const double >::type aD(aDSEXP);
    Rcpp::traits::input_parameter< bool >::type return_sparse(return_sparseSEXP);
    Rcpp::traits::input_parameter< bool >::type calc_zeros(calc_zerosSEXP);
    rcpp_result_gen = Rcpp::wrap(vstExprsCPP(a, eP, aD, return_sparse, calc_zeros));
    return rcpp_result_gen;
END_RCPP
}
// iterateSparseMatrixCPP
void iterateSparseMatrixCPP(const arma::sp_mat& a);
RcppExport SEXP _m3addon_iterateSparseMatrixCPP(SEXP aSEXP) {
BEGIN_RCPP
    Rcpp::RNGScope rcpp_rngScope_gen;
    Rcpp::traits::input_parameter< const arma::sp_mat& >::type a(aSEXP);
    iterateSparseMatrixCPP(a);
    return R_NilValue;
END_RCPP
}

static const R_CallMethodDef CallEntries[] = {
    {"_m3addon_sp_show_storage", (DL_FUNC) &_m3addon_sp_show_storage, 1},
    {"_m3addon_subsetSM", (DL_FUNC) &_m3addon_subsetSM, 3},
    {"_m3addon_calculateScoresCPP", (DL_FUNC) &_m3addon_calculateScoresCPP, 2},
    {"_m3addon_logNormCPP", (DL_FUNC) &_m3addon_logNormCPP, 1},
    {"_m3addon_colStdDev", (DL_FUNC) &_m3addon_colStdDev, 1},
    {"_m3addon_rowStdDev", (DL_FUNC) &_m3addon_rowStdDev, 1},
    {"_m3addon_vstExprsCPP", (DL_FUNC) &_m3addon_vstExprsCPP, 5},
    {"_m3addon_iterateSparseMatrixCPP", (DL_FUNC) &_m3addon_iterateSparseMatrixCPP, 1},
    {NULL, NULL, 0}
};

RcppExport void R_init_m3addon(DllInfo *dll) {
    R_registerRoutines(dll, NULL, CallEntries, NULL, NULL);
    R_useDynamicSymbols(dll, FALSE);
}