# Using the transformation

```
# read in `h_n2ddt_transformation` from `n2ddt.root`
rh_8 = the_current_rho;
n_rho_bins = h_n2ddt_transformation.GetXaxis().GetNbins();

# get the rho bin
rho_index = h_n2ddt_transformation.GetXaxis().FindBin(rh_8) - 1;

# if boundary conditions
if rh_8 > h_n2ddt_transformation.GetXaxis().GetBinUpEdge( n_rho_bins ): rho_index = n_rho_bins-1;
if rh_8 < h_n2ddt_transformation.GetXaxis().GetBinLowEdge( 1 ): rho_index = 0;

# transform N2
jtN2b1sdddt_8 = jtN2b1sd_8 - quantile[rho_index] + (9.0e-05)*(jpt_8-500.);
```