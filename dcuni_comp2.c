#include"TCanvas.h"
#include"TGraphErrors.h"
#include"TFile.h"
#include"TF1.h"
#include"TCanvas.h"
#include"TH1.h"
#include"TH2.h"
#include"TLegend.h"
#include"TArrow.h"
#include"TLatex.h"
#include"TSystemDirectory.h"
#include"TDirectory.h"
#include"TKey.h"

#include <fstream>
#include <iostream>
#include <cstdio>
#include <unistd.h>
#include <utility>
#include <vector>
#include <algorithm>
#include <sstream>
#include <functional>
#include <string>
#include <numeric>

//
//  Jack W King AAS BA BE(May 2016) 02/26/2016
//

int eff( string newmod, string fileDesg ){

        cout << "Starting Efficency Script" << endl;

        cout << "Usage:  eff( module_name_string , starting_hr_file_string )" << endl;
        cout << "for defaults enter \"hr\" for starting hr file designator. " << endl;

        char chpath[256];
        getcwd(chpath, 255);
	std::string inst("KU");  ///<<<<<<<<<<<<<<<<<<SET INSTITUTE STRING ( inst )  TO CORECT INSTITUTE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        std::string path(chpath);
        std::string mod("paXXX");//<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 
        if( newmod != "" )  mod = newmod;
        // <<<<<< change folder/module name to run in 
        //std::string mod("yhc691015sn3p35");
        
        std::string dataPath =  path + "/" + mod + "data";
        //std::string measurementFolder =  mod + "data";
        std::string configPath = path + "/" + mod;
        std::string HighRateSaveFileName( "Results_Hr" );
        std::string HighRateFileName( "hr" );//<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	std::string phRunFileName( "ph" );
	if( inst != "KU" ) phRunFileName = "dc";
        if( fileDesg != "" ) HighRateFileName = fileDesg;
        int hrnamelength = HighRateFileName.length();
	int phnamelength = phRunFileName.length();

	// <<<<<<<<<<<<<<<<<<<  change Highrate File name to use
    	//  assumes something like hr08ma_pa225_082715.root
    	//  10 or 08 or 06 or 04 or 02 required after hr
    	//      --   looks for a root file  with "HighRateFileName" followed by 10 or 08 or ect....
    	//      --   so will parse hr10****.root and hr08**********.root ect...  with above settings
    	std::string moduleName = mod;

	std::string maskFileName("defaultMaskFile.dat");

	const bool FIDUCIAL_ONLY = true; // don't change
	const bool VERBOSE = true;

	int nTrigPerPixel = 50; // will be read from testParameters.dat
	int nPixels = 4160;
	int nTrig = nTrigPerPixel * nPixels;
	float pixelArea = 0.01 * 0.015; // cm^2
	float triggerDuration = 25e-9; //s

	const int nRocs = 16;
	const int nDCol = 25;
	
	double worstDCol[nRocs];
	for( int i = 0; i<nRocs; i++) worstDCol[i] = -1;
	double worstDColEff[nRocs];
        for( int i = 0; i<nRocs; i++) worstDColEff[i] = 10;

	double bestDCol[nRocs];
        for( int i = 0; i<nRocs; i++) bestDCol[i] = -1;
        double bestDColEff[nRocs];
        for( int i = 0; i<nRocs; i++) bestDColEff[i] = 10;

	double lowestdceff = 10;
        int lowestdc = -1;
        int lowestroc = 25;

        double highdceff = -10;
        int highdc = -1;
        int highroc = 25;

	std::string directoryList = mod;

	std::string outFileName = dataPath + "/" + HighRateFileName + "Efficiency.log";
        std::ofstream log(outFileName.c_str());


	cout << "search for HREfficiency folders in elComandante folder structure" << endl;
    	log << "High Rate Efficency Log File Module: "<< mod << endl << endl;
	TSystemDirectory dir(dataPath.c_str(), dataPath.c_str());
    	TList *files = dir.GetListOfFiles();
    	std::vector<std::string> fileList;
    	if (files) {
      		TSystemFile *file;
      		TString fname;
      		TIter next(files);
      		while ((file=(TSystemFile*)next())) {
        		fname = file->GetName();
			std::cout << fname << endl;
         		std::string filename = fname.Data();
			if (filename.substr(0,hrnamelength) == HighRateFileName ) {
				if( filename.substr(( filename.length() - 4 ), 4)  == "root" ){
         				fileList.push_back(filename);
					std::cout << "---Added to fileList" << endl;
				}
			}
			if (filename.substr(0,phnamelength) == phRunFileName ) {
                                if( filename.substr(( filename.length() - 4 ), 4)  == "root" ){
                                        fileList.push_back(filename);
                                        std::cout << "---Added to fileList" << endl;
				}
         		}
      		}
    	}


        std::vector<double> ylist;
	if( inst == "KU" ){
        	ylist.push_back(1.0);
        	ylist.push_back(0.8);
        	ylist.push_back(0.6);
        	ylist.push_back(0.4);
        	ylist.push_back(0.2);
	} else {
	        ylist.push_back(0.05);
        	ylist.push_back(0.10);
        	ylist.push_back(0.15);
	}

	std::cout << " Declaring vectors" << endl;
        
	double rocratehigh[nRocs];
       	double rocratelow[nRocs];

    	std::vector< std::vector< std::pair< int,int > > > maskedPixels;
	std::vector< std::vector< double > > efficiencies;
	std::vector< std::vector< double > > efficiencyErrors;
	std::vector< std::vector< double > > rates;
	std::vector< std::vector< double > > rateErrors;
	std::vector< double > hitslow;
	std::vector< double > hitshigh;
        std::vector< double > phhitslow;
        std::vector< double > phhitshigh;
	std::vector< double > efflow;
	std::vector< double > effhigh;
        std::vector< double > DCUni;
        std::vector< double > DCUniNum;
   	std::vector< double > phDCUni;
        std::vector< double > phDCUniNum;
	std::vector< double > Uni;

	std::vector< std::vector< std::vector< double > > > dcolHits;
	std::vector< std::vector< std::vector< double > > > dcolHitErrors;
	std::vector< std::vector< std::vector< double > > > dcolRates;
        std::vector< std::vector< std::vector< double > > > dcolRateErrors;
        std::vector< std::vector< std::vector< double > > > dcolEff;
        std::vector< std::vector< std::vector< double > > > dcolEffErrors;

	std::vector< std::vector< double > > lineList;
	std::vector<std::vector<double>> dclineList;	

	std::vector< std::vector< double > > bigempty; 
	std::vector< double > empty;

	std::cout << " Line Lists" << endl;
	for( int i=0; i <4; i++ ){
		lineList.push_back(empty);
		dclineList.push_back(empty);
	}

	for( int i = 0; i<201;i++){
		lineList[1].push_back(.98);
		lineList[0].push_back(i);
	}

	for( int i = 0; i<= 100; i++ ){
		lineList[3].push_back(i/100);
		lineList[2].push_back(120.0);
	} 

	for( int i = 0; i <= 450; i++){
		dclineList[1].push_back(1.5);
                dclineList[0].push_back(i);
		dclineList[3].push_back(0.6);
                dclineList[2].push_back(i);
	}


	for (int i=0;i<=nRocs;i++) {
		efficiencies.push_back(empty);
		efficiencyErrors.push_back(empty);
		rates.push_back(empty);
		rateErrors.push_back(empty);
		dcolHits.push_back(bigempty);
         	dcolHitErrors.push_back(bigempty);
	        dcolRates.push_back(bigempty);
                dcolRateErrors.push_back(bigempty);
                dcolEff.push_back(bigempty);
                dcolEffErrors.push_back(bigempty);
	 }

	int dc98count[nRocs][nDCol];
	int dc95count[nRocs][nDCol];
	int totdc98 = 0;
	int totdc95 = 0;

        int dc08count[nRocs][nDCol];
        int dc12count[nRocs][nDCol];
        int totdc08 = 0;
        int totdc12 = 0;
	
	int dcbothcount[nRocs][nDCol];
	int totdcboth = 0;


        for( int i=0; i<nRocs; i++){
                for( int j=0; j<nDCol; j++){
                        dc98count[i][j] = 0;
                        dc95count[i][j] = 0;
                        dc08count[i][j] = 0;
                        dc12count[i][j] = 0;
			dcbothcount[i][j] = 0;
                }
        }

	for( int i=0; i<=nRocs; i++){
		for( int j=0; j<=nDCol; j++){
			dcolHits[i].push_back(empty);
			dcolHitErrors[i].push_back(empty);
	                dcolRates[i].push_back(empty);
	                dcolRateErrors[i].push_back(empty);
                	dcolEff[i].push_back(empty);
                	dcolEffErrors[i].push_back(empty);
		}
	}


	std::cout << "loop over all commander_HREfficiency.root root files" << endl;
	for (int i=0;i<1;++i) {
		chdir(path.c_str());
		std::cout << "looking in directory <" << directoryList << ">" << std::endl;
		std::cout << "From " << path << endl;
		std::string parmFile = directoryList + "/testParameters.dat";
		cout << "For " << parmFile << endl;
		std::ifstream testParameters(parmFile.c_str());
		std::string line2;
		cout << "Getting line" << endl;
	
		while (getline(testParameters, line2)) {
			cout << line2 << endl;
			if (line2.find("HighRate") != std::string::npos) {
				while (getline(testParameters, line2)) {
					if (line2.size() < 1) break;
					size_t pos = line2.find("Ntrig");
					std::cout << line2 << " " << pos << endl;
					if (pos != std::string::npos) {
						nTrigPerPixel = atoi(line2.substr(pos+6).c_str());
						nTrig = nTrigPerPixel * nPixels;
						std::cout << ">" << line2 << "< pos:" << pos << std::endl;
						std::cout << "number of triggers per pixel: " << nTrigPerPixel << std::endl;
					}
				}

			}
		}
		testParameters.close();


		// read masked pixels
	    	maskedPixels.clear();
		for (int j=0;j<nRocs;j++) {
			std::vector< std::pair<int,int> > rocMaskedPixels;
			maskedPixels.push_back(rocMaskedPixels);
		}
		std::ifstream maskFile;
		char maskFilePath[256];
		sprintf(maskFilePath, "%s/%s/%s", path.c_str(), directoryList.c_str(), maskFileName.c_str());
		maskFile.open(maskFilePath, std::ifstream::in);
		if (!maskFile) {
			std::cout << "ERROR: mask file <" << maskFilePath << "> can't be opened!"<<std::endl;
		}
		std::string line;
		std::vector< std::string > tokens;
		while(getline(maskFile, line)) {
			if (line[0] != '#') {
				std::stringstream ss(line); 
	    			std::string buf;
	    			tokens.clear();
				while (ss >> buf) {
					tokens.push_back(buf);
				}
				std::cout << "tok0 <" << tokens[0] << "> ";
				if (tokens[0] == "pix" && tokens.size() >= 4) {
					int roc = atoi(tokens[1].c_str());
					int col = atoi(tokens[2].c_str());
					int row = atoi(tokens[3].c_str());
					std::cout << "mask pixel " << roc << " " << col << " " << row << std::endl;
					maskedPixels[roc].push_back(std::make_pair(col, row));
				}
			}
		}
		maskFile.close();
	}

	chdir( dataPath.c_str() );
        int len = fileList.size();
	std::string blank(" ");
	std::vector< std::string > listTFile;
	listTFile.push_back( blank );
        listTFile.push_back( blank );
        listTFile.push_back( blank );
        listTFile.push_back( blank );
        listTFile.push_back( blank );
	listTFile.push_back( blank );
        listTFile.push_back( blank );
	
	cout << "Sorting T file list " << endl;
	
	int low = 0;
	int high = 0;
	for( int i=0; i<len; i++){

		std::string currentRootFile = fileList[i];
		std::string fileType = currentRootFile.substr(0,hrnamelength);
		if( fileType == HighRateFileName ){		
			std::string fileRate = currentRootFile.substr(hrnamelength,2);
			std::cout<< " Looking for: " << fileRate << endl;
			int rateIndex = 100;
			if( inst == "KU" ){
				if(fileRate == "10") { rateIndex = 0;}
				else if( fileRate == "08"){ rateIndex = 1;}
				else if( fileRate == "06"){ rateIndex = 2;}
				else if( fileRate == "04"){ rateIndex = 3;}
				else if( fileRate == "02"){ rateIndex = 4;}
				else {
					std::cout << "could not read rate: " << currentRootFile << " .";
					exit(0);
				}
			} else {
				if(fileRate == "05") { rateIndex = 0;}
                        	else if( fileRate == "10"){ rateIndex = 1;}
                        	else if( fileRate == "15"){ rateIndex = 2;}
                        	else {
                                	std::cout << "could not read rate: " << currentRootFile << " .";
                                	exit(0);
                        	}
			}
			listTFile[rateIndex]=currentRootFile;
		} else {
                        std::string fileRate = currentRootFile.substr(phnamelength,2);
                        std::cout<< " Looking for: " << fileRate << endl;
                        int rateIndex = 100;
                        if( inst == "KU" ){
                                if(fileRate == "02") { rateIndex = 5; low = 5; }
                                else if( fileRate == "06"){ rateIndex = 6; high = 6; }
                                else {
                                        std::cout << "could not read rate: " << currentRootFile << " .";
                                        exit(0);
                                }
                        } else {
                                if(fileRate == "05") { rateIndex = 3; low = 3; }
                                else if( fileRate == "15"){ rateIndex = 4; high = 4; }
                                else {
                                        std::cout << "could not read rate: " << currentRootFile << " .";
                                        exit(0);
                                }
                        }
                        listTFile[rateIndex]=currentRootFile;
		}
	}

   // here use the phrun files
    //
    //
    std::string phLowName = listTFile[low];
    std::string phHighName = listTFile[high];

    //int rateIndex = 0;
    //int dColModCount =0;
    TFile lowTfile( phLowName.c_str() );
    std::cout << "Working file : " << phLowName << endl;
    TFile highTfile( phHighName.c_str() );
    std::cout << "Working file : " << phHighName << endl;

    TH2D* lowphmap;
    TH2D* highphmap;
    char h_phlowName[256];
    char h_phhighName[256];
    double rocPHratehigh[nRocs];
    double rocPHratelow[nRocs];
    //double rocratehits = 0;
    //double rocratenum = 0;
    std::ofstream output;
    for (int iRoc=0;iRoc<nRocs;iRoc++) {
        sprintf( h_phlowName, "Xray/hMap_02ma_C%d_V0;1", iRoc);
        sprintf( h_phhighName, "Xray/hMap_06ma_C%d_V0;1", iRoc);
        lowTfile.GetObject(h_phlowName, lowphmap);
        highTfile.GetObject(h_phhighName,highphmap);
        if (lowphmap == 0) {
            std::cout << "ERROR: phlow-ray hitmap not found!" << std::endl;
        }
        if (highphmap == 0) {
            std::cout << "ERROR: phhigh-ray hitmap not found!" << std::endl;
        }
        int nBinsX = lowphmap->GetXaxis()->GetNbins();
        int nBinsY = lowphmap->GetYaxis()->GetNbins();
        std::vector<double> roc_lowPHhits;
        std::vector<double> roc_highPHhits;
        //int done = 0;
        //double totRPixs = 0;
        //double totRHits = 0;
        int deadPixs = 0;
        //std::cout << nBinsX << "x" << nBinsY << std::endl;
        for (int dcol = 0; dcol < nDCol; dcol++) {
            //std::vector<double> hits;
            std::vector<double> phlow_hits;
            std::vector<double> phhigh_hits;
            double totLowHits = 0;
            double totHighHits = 0;

           for (int y = 0; y < 160; y++) {
                bool masked = false;
                //std::cout << " Masking " << endl;
                for (int iMaskedPixels=0; iMaskedPixels < maskedPixels[iRoc].size(); iMaskedPixels++) {
                int locFirst = dcol * 2 + (int)(y/80);
                int locSecond = y%80;
                if ( (maskedPixels[iRoc][iMaskedPixels].first == locFirst) && (maskedPixels[iRoc][iMaskedPixels].second == locSecond)) {
                    masked = true;
                    break;
                    }
                }

               if ((!FIDUCIAL_ONLY || ((y % 80) > 0 && (y % 80) < 79)) && !masked) {
                   //std::cout << " get " << (dcol * 2 + (int)(y / 80) + 1) << " / " <<  ((y % 80) + 1) << std::endl;
                   double low_trans = 0;
                   double high_trans= 0;
                   low_trans =  lowphmap->GetBinContent(dcol * 2 + (int)(y / 80) + 1, (y % 80) + 1);
                   high_trans = highphmap->GetBinContent(dcol * 2 + (int)(y / 80) + 1, (y % 80) + 1);
                   if( low_trans == 0){ deadPixs++; phlow_hits.push_back(0.0), phhigh_hits.push_back(0.0);}
                   else {
                       phlow_hits.push_back( low_trans );
                       totLowHits += low_trans;
                       phhigh_hits.push_back( high_trans);
                       totHighHits += high_trans;
                        }
               }//if fiducial
               roc_lowPHhits.push_back(totLowHits);
               roc_highPHhits.push_back( totHighHits);

           }//for y

            int dclownum = roc_lowPHhits.size();
            int dchighnum = roc_highPHhits.size();
         //}//for dc
         phhitshigh.push_back(totHighHits);
         phhitslow.push_back(totLowHits);


         }
         rocPHratelow[iRoc]  = TMath::Mean( dclownum, &roc_lowPHhits[0] ) / (nTrig * triggerDuration * pixelArea) * 1.0e-6;
         rocPHratehigh[iRoc]  = TMath::Mean( dchighnum, &roc_highPHhits[0] ) / (nTrig * triggerDuration * pixelArea) * 1.0e-6;


    }

    ///
    ///
    ///
    ///
    ///
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////PROCESSING START/////////////////////////////////////
	std::cout<< "Processing  HR files: quanity: " << len << endl;	                                
	log << "Double Column's with Efficency < 98 % under 120 MHz/cm^2" << endl;
	for (int i=0; i<len ; ++i) {

		int rateIndex = 0;		
                int dColModCount = 0;

		std::string currentRootFile = listTFile[i];	
		std::cout << "Working file : " << currentRootFile << endl;

		TFile curTfile(currentRootFile.c_str());
		if (curTfile.IsZombie()) {
			std::cout << "could not read: " << currentRootFile << " .";
			exit(0);
		}

		std::cout << "list keys:" << std::endl;
		TIter next(curTfile.GetListOfKeys());
		bool highRateFound = false;
	
		TKey *obj;
		while ( (obj = (TKey*)next()) ) {
			if ((strcmp(obj->GetTitle(),"HighRate") == 0) || (strcmp(obj->GetTitle(),"Xray") == 0))  highRateFound = true;
			if (VERBOSE) {
				std::cout << obj->GetTitle() << std::endl;
			}
		}
		if (highRateFound) {
			std::cout << "highRate test found, reading data..." << std::endl;
			TH2D* xraymap;
			TH2D* calmap;
			char calmapName[256];
			char xraymapName[256];
			double rocratehits = 0;
			double rocratenum = 0;
			std::ofstream output;
           
			std::cout << "calculating rates and efficiencies" << std::endl;

			for (int iRoc=0;iRoc<nRocs;iRoc++) {

				int nBinsX = 0; //xraymap->GetXaxis()->GetNbins();
                                int nBinsY = 0; //xraymap->GetYaxis()->GetNbins();				

				if( i < ( len-2) ){
					//std::cout << "ROC" << iRoc << std::endl;        //                         to move to single root file:  use same file name all files;
					sprintf(xraymapName, "HighRate/highRate_xraymap_C%d_V0;1", iRoc);
						//<<  add index to "V0" "V1" ect string say:string version[3]; = {"V0", "V1", "V2"}  sync file index
					curTfile.GetObject(xraymapName, xraymap);
					if (xraymap == 0) {
						std::cout << "ERROR: x-ray hitmap not found!" << std::endl;
					}
					nBinsX = xraymap->GetXaxis()->GetNbins();
					nBinsY = xraymap->GetYaxis()->GetNbins();
				
					sprintf(calmapName, "HighRate/highRate_C%d_V0;1", iRoc);//<<<<  do same thing as above<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
					curTfile.GetObject(calmapName, calmap);
					if (calmap == 0) {
						sprintf(calmapName, "HighRate/highRate_calmap_C%d_V0;1", iRoc);
						curTfile.GetObject(calmapName, calmap);
						if (calmap == 0) {
							std::cout << "ERROR: calibration hitmap not found!" << std::endl;
						}
					}
				} else {
					if( inst == "KU" ) { 
						if( i == low ){ sprintf(xraymapName, "Xray/hMap_02ma_C%d_V0;1", iRoc);} else {sprintf(xraymapName, "Xray/hMap_06ma_C%d_V0;1", iRoc);}
					}
					else { 
						if( i == low ) { sprintf(xraymapName, "Xray/hMap_DCLowRate_C%d_V0", iRoc); } else { sprintf(xraymapName, "Xray/hMap_DCHighRate_C%d_V0", iRoc); }
					}
                                        curTfile.GetObject(xraymapName, xraymap);
                                        if (xraymap == 0) {
                                                std::cout << "ERROR: x-ray hitmap not found!" << std::endl;
                                        }
                                        nBinsX = xraymap->GetXaxis()->GetNbins();
                                        nBinsY = xraymap->GetYaxis()->GetNbins();
					calmap = xraymap;
                                }

				std::vector<double> roc_xhits;
				double totRPixs = 0;
				double totRHits = 0;
				int deadPixs = 0;
  //              		int badBumps = 0;
				//std::cout << nBinsX << "x" << nBinsY << std::endl;
				for (int dcol = 0; dcol < nDCol; dcol++) {
					std::cout << "reading dc " << dcol << std::endl;

					std::vector<double> hits;
					std::vector<double> xray_hits;
					int done = 0;
					double totCHits = 0;
					double totXHits = 0;
 					double rate = 0;
                                        double efficiency = 0;
                                        double rateError = 0;
                                        double efficiencyError = 0;

					std::cout<<"Getting data from Histograms" << endl;

					for (int y = 0; y < 160; y++) {

						bool masked = false;
						//std::cout << " Masking " << endl;
						for (int iMaskedPixels=0; iMaskedPixels < maskedPixels[iRoc].size(); iMaskedPixels++) {
							int locFirst = dcol * 2 + (int)(y/80);
							int locSecond = y%80;
							if ( (maskedPixels[iRoc][iMaskedPixels].first == locFirst) && (maskedPixels[iRoc][iMaskedPixels].second == locSecond)) {
								masked = true;
								break;
							}
						}

						if ((!FIDUCIAL_ONLY || ((y % 80) > 0 && (y % 80) < 79)) && !masked) {
							//std::cout << " get " << (dcol * 2 + (int)(y / 80) + 1) << " / " <<  ((y % 80) + 1) << std::endl;
							double ctrans = 0;
							double xtrans = 0;
							ctrans =  calmap->GetBinContent(dcol * 2 + (int)(y / 80) + 1, (y % 80) + 1);
							xtrans = xraymap->GetBinContent(dcol * 2 + (int)(y / 80) + 1, (y % 80) + 1);
							if( ctrans == 0 ){ deadPixs++; }
//                            				else if ( xtrans == 0 ){ badBumps++; }
							else {
								hits.push_back(ctrans);
                                                        	totCHits += ctrans;
								xray_hits.push_back( xtrans );
								totXHits += xtrans; }
						}
					}
					

					int nPixelsDC = hits.size();
	//				cout << "Deadpixs: " << deadPixs << endl;
 					if(nPixelsDC < 1) nPixelsDC = 1;					
	//				cout << " set nPixelsDC < 1 to 1" << endl;
					if( totXHits > 0 ){ 
						totRHits = TMath::Mean(nPixelsDC, &xray_hits[0]);
						rate = TMath::Mean(nPixelsDC, &xray_hits[0]) / (nTrig * triggerDuration * pixelArea) * 1.0e-6;
                                        	rateError = TMath::RMS(nPixelsDC, &xray_hits[0]) / std::sqrt(nPixelsDC) / (nTrig * triggerDuration * pixelArea) * 1.0e-6;
					}else{ 
						totRHits = 0;
						rate = 0;
						rateError = 0;
					}
					if( totCHits > 0 ){
                                                efficiency = TMath::Mean(nPixelsDC, &hits[0]) / nTrigPerPixel;
                                                efficiencyError = TMath::RMS(nPixelsDC, &hits[0]) / std::sqrt(nPixelsDC) / nTrigPerPixel;
                                        }else{ 
                                                efficiency = 0; 
                                                efficiencyError = 0;
                                        }

	//				cout << " found totRHits " << endl;
					rocratehits += totXHits;
					rocratenum += nPixelsDC;
	//				cout << "counted totals for xhits" << endl;
					roc_xhits.push_back( totRHits );
					
					cout << "Assigning vales" << endl;
					if( i < low ){
						efficiencies[iRoc].push_back(efficiency);
						efficiencyErrors[iRoc].push_back(efficiencyError);
						rates[iRoc].push_back(rate);
						rateErrors[iRoc].push_back(rateError);
                                        	dcolHits[iRoc][dcol].push_back(totXHits);
                                        	dcolHitErrors[iRoc][dcol].push_back(std::sqrt(totXHits));
						dcolEff[iRoc][dcol].push_back(efficiency);
						dcolEffErrors[iRoc][dcol].push_back(efficiencyError);
						dcolRates[iRoc][dcol].push_back(rate);
                                        	dcolRateErrors[iRoc][dcol].push_back(rateError);

                                        	efficiencies[nRocs].push_back(efficiency);
                                        	efficiencyErrors[nRocs].push_back(efficiencyError);
                                        	rates[nRocs].push_back(rate);
                                        	rateErrors[nRocs].push_back(rateError);
						dcolRates[nRocs][0].push_back(rate);
						dcolRates[nRocs][1].push_back(dColModCount);		
			
					
						dColModCount++;	
					}	

	//				cout << " finding filtered values" << endl;
					if( ( i == 0 ) && rate < 120 ){
                                                done = 1;
                                                if( efficiency < worstDColEff[iRoc] ){
                                                        worstDColEff[iRoc] = efficiency;
                                                        worstDCol[iRoc] = dcol;
                                                }
                                        } else if( ( done = 0 ) && ( i == 1 ) && ( rate < 120 ) ){
                                                if( iRoc == nRocs-1 ) done = 1;
                                                if( efficiency < worstDColEff[iRoc] ){
                                                        worstDColEff[iRoc] = efficiency;
                                                        worstDCol[iRoc] = dcol;
                                                }
                                        } else if( ( done = 0 ) && ( i == 2 ) && ( rate < 120 ) ){
                                                 if( iRoc == nRocs-1 ) done = 1;
                                                if( efficiency < worstDColEff[iRoc] ){
                                                        worstDColEff[iRoc] = efficiency;
                                                        worstDCol[iRoc] = dcol;
                                                }
                                        }
					if( ( efficiency < bestDColEff[iRoc]) && ( i == (low-1)) ) {
                                                bestDColEff[iRoc] = efficiency;
                                                bestDCol[iRoc] = dcol;
                                        }
					if( i == low ){ hitslow.push_back(totXHits);}
					if( i == (low - 1) ){	efflow.push_back(totCHits);}
					if( i == high ){ hitshigh.push_back(totXHits);}
					if( i == 1 ){	effhigh.push_back(totCHits); }     
					if( i < low ){
						if( efficiency < 0.98 && rate < 120 ){	
							dc98count[iRoc][dcol] = 1;
							log << "Roc: " << iRoc << " dc: " << dcol << " rate: " << rate << " eff: " << efficiency << std::endl;
						}
						if( efficiency < 0.95 && rate < 120 ){
							dc95count[iRoc][dcol] = 1;
						}
						if (VERBOSE) {
							std::cout << "Roc " << iRoc << " dc " << dcol << " nPixelsDC: " << nPixelsDC << " rate: " << rate << " " << efficiency << std::endl;
						}
					}
				}
				if( i == low ){
					int dcnum = roc_xhits.size();
	//				cout << "in len-1"<<endl;
					rocratelow[iRoc]  = TMath::Mean( dcnum, &roc_xhits[0] ) / (nTrig * triggerDuration * pixelArea) * 1.0e-6;
//	log << "Rate low Roc: " << iRoc << " : " << rocratelow[iRoc] << " : totals : " << (rocratehits/rocratenum)/(nTrig * triggerDuration * pixelArea) * 1.0e-6 << endl; 
				}
				if( i == high ){
	//				cout << "in 1" << endl;
                                        int dcnum = roc_xhits.size();
                                        rocratehigh[iRoc]  = TMath::Mean( dcnum, &roc_xhits[0] ) / (nTrig * triggerDuration * pixelArea) * 1.0e-6; 
//	log << "Rate high Roc: " << iRoc << " : " << rocratehigh[iRoc] << " : totals : " << (rocratehits/rocratenum)/(nTrig * triggerDuration * pixelArea) * 1.0e-6 << endl;
				}
			}
//
		} else {
		cout << "high rate test not found" << std::endl;
		return 1;
		}
		cout << "end of Data Collection" << endl;
	}
/////////////////////////////////////////////////////////////////////////////////////////Calc Output values not calculated in datainput////////////////////////////////////////////////////
	std::cout << "Output Phase" << std::endl;

	std::ofstream outfile("efficiency.csv");
        std::vector<double> slopes;
        std::vector<double> slope_err;

	int dc = 0;
	double lowUni = 2.0;
	double highUni = 0.0;
	int lowUDC = 0;
	int highUDC = 0;
	double udceff = 0;
	double phudceff = 0;
	
	log << endl;

	for (int iRoc=0;iRoc<nRocs;iRoc++) {

		for( int j=0; j<nDCol; j++){
                        dc = (iRoc*nDCol)+j;
			if( hitshigh[dc] < 0 ) hitshigh[dc] = 0;
			if( hitslow[dc] <= 0 ) hitslow[dc] = 1;
			if( rocratehigh[iRoc] <= 0 ) rocratehigh[iRoc] = 1;
			if( rocratelow[iRoc] < 0 ) rocratelow[iRoc] = 0;
                        udceff =  hitshigh[dc] / hitslow[dc] / rocratehigh[iRoc] * rocratelow[iRoc];
			if( udceff < 0 ) udceff = 0;
                        DCUni.push_back(udceff);
                        DCUniNum.push_back(dc);
                        if( udceff < lowUni ){ lowUni = udceff; lowUDC = dc; }
                        if( udceff > highUni ){ highUni = udceff; highUDC = dc; }
			if( udceff >= 1.5 ) dc12count[iRoc][j] = 1;
			if( udceff <= 0.6 ) dc08count[iRoc][j] = 1;
			if( dc98count[iRoc][j] == 1  && ( dc12count[iRoc][j] == 1 || dc08count[iRoc][j] == 1 ) ) dcbothcount[iRoc][j] = 1;
//			log << "rate for roc " << iRoc << " high " << rocratehigh[iRoc] << " low " << rocratelow[iRoc] << endl;
//                }

  //              for( int j=0; j<nDCol; j++){
    //                    dc = (iRoc*nDCol)+j;
                        if( phhitshigh[dc] < 0 ) phhitshigh[dc] = 0;
                        if( phhitslow[dc] <= 0 ) phhitslow[dc] = 1;
      //                  if( rocratehigh[iRoc] <= 0 ) rocratehigh[iRoc] = 1;
        //                if( rocratelow[iRoc] < 0 ) rocratelow[iRoc] = 1;
                        std::cout << "dl"<< dc << "roc"<< iRoc << "hitshigh" << hitshigh[dc] << "hitslow" <<hitslow[dc] << "rate high" << rocPHratehigh[iRoc] << "rate low" <<rocPHratelow[iRoc] << endl;
                        phudceff =  0.1* phhitshigh[dc] / phhitslow[dc] / rocPHratelow[iRoc] * rocPHratehigh[iRoc];
         //               std::cout << "udceff" << phudceff << std::endl;
                        if( phudceff < 0 ) phudceff = 0;
                        phDCUni.push_back(udceff);
                        phDCUniNum.push_back(dc);
                       // if( udceff < lowUni ){ lowUni = udceff; lowUDC = dc; }
                        //if( udceff > highUni ){ highUni = udceff; highUDC = dc; }
                        //if( udceff >= 1.5 ) dc12count[iRoc][j] = 1;
                        //if( udceff <= 0.6 ) dc08count[iRoc][j] = 1;
                        //if( dc98count[iRoc][j] == 1  && ( dc12count[iRoc][j] == 1 || dc08count[iRoc][j] == 1 ) ) dcbothcount[iRoc][j] = 1;
//                      log << "rate for roc " << iRoc << " high " << rocratehigh[iRoc] << " low " << rocratelow[iRoc] << endl;
                }

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////OUTPUT START////////////////////////////////////////////////////

		std::cout << "Working in ROC " << iRoc << endl;
/*		TCanvas *c1 = new TCanvas("c1", "efficiency", 200, 10, 700, 500);
		c1->Range(0,0,1, 300);
		TGraphErrors* TGE = new TGraphErrors( rates[iRoc].size(), &rates[iRoc][0], &efficiencies[iRoc][0], &rateErrors[iRoc][0] , &efficiencyErrors[iRoc][0] ) ;
		TGraph* tge2 = new TGraph( lineList[0].size(), &lineList[0][0], &lineList[1][0] );
                TGraph* tge3 = new TGraph( lineList[2].size(), &lineList[2][0], &lineList[3][0] );

		char graphTitle[256];
		sprintf(graphTitle, "Fiducial Efficiency vs Rate for %s ROC %d", moduleName.c_str(), iRoc);
		TGE->SetTitle(graphTitle);
		TGE->SetMarkerStyle(3);
		TGE->SetMarkerSize(1);
		TGE->GetXaxis()->SetTitle("Rate: MHz/cm^2");
		TGE->GetYaxis()->SetTitle("Efficency 1.00 = 100%");
		TGE->Draw("ap");
		
		tge2->SetMarkerColor( kRed );
		tge2->SetMarkerStyle(21);
 
		tge3->SetMarkerColor( kRed );
		tge3->SetMarkerStyle(21);

		TF1* myfit = new TF1("fitfun", "([0]-[1]*x*x*x)", 20, 140);
		myfit->SetParameter(0, 1);
		myfit->SetParLimits(0, 0.9, 1.1);
		myfit->SetParameter(1, 5e-9);
		myfit->SetParLimits(1, 1e-10, 5e-8);			
	
		tge2->Draw("same");
		tge3->Draw("same");	
		TGE->Fit(myfit, "BR");
		c1->Update();
		
		double p0= myfit->GetParameter(0);
		double p1= myfit->GetParameter(1);
		double p0_err = myfit->GetParError(0);
		double p1_err = myfit->GetParError(1);
		double eff_err = sqrt(p0_err * p0_err + pow(120.0,6) * p1_err * p1_err);
		outfile << (p0 - p1 * 120*120*120) << std::endl;
		log << "Estimated Effiency at 120MHz/cm^2 for ROC:" << iRoc << " Eff: " << p0-p1 *120*120*120 << " +/- " << eff_err << endl; 
		log << "Lowest DC Eff at High Rate for  ROC:" << iRoc << "  DC :" << worstDCol[iRoc] << " Eff: " << worstDColEff[iRoc] << endl;
                log << "Lowest DC Eff at Low Rate for  ROC:" << iRoc << "  DC :" << bestDCol[iRoc] <<  " Eff: " << bestDColEff[iRoc] << endl;
                log << "Highest  DC Uni  for  ROC:" << iRoc << "  DC :" << highUDC << " Uniformity: " << highUni << endl;
                log << "Lowest DC Uni for  ROC:" << iRoc << "  DC :" << lowUDC <<  " Uniformity: " << lowUni << endl;

		if( worstDColEff[iRoc] < lowestdceff ){
			lowestdceff = worstDColEff[iRoc];
			lowestdc = worstDCol[iRoc];
			lowestroc = iRoc;
		}

		if( bestDColEff[iRoc] > highdceff ){
                        highdceff = bestDColEff[iRoc];
                        highdc = bestDCol[iRoc];
                        highroc = iRoc;
                }

		c1->Modified();
		gPad->Modified();
		char saveFileName[256];
		sprintf(saveFileName, "%s_Eff_C%d.png",HighRateSaveFileName.c_str(), iRoc);
		c1->SaveAs(saveFileName);
		c1->Clear();
		TGE->Clear();

		myfit->Clear();
		delete myfit;
		delete c1;
*/
/*		TCanvas *c3 = new TCanvas("c3", "worst_dcol", 200, 10, 700, 500);
                c3->Range(0,0,1, 300);
		int use = worstDCol[iRoc];
                TGraphErrors* TGE2 = new TGraphErrors(dcolEff[iRoc][use].size(), &dcolRates[iRoc][use][0], &dcolEff[iRoc][use][0], &dcolRateErrors[iRoc][use][0] , &dcolEffErrors[iRoc][use][0]);
                TGraph* tge4 = new TGraph( lineList[0].size(), &lineList[0][0], &lineList[1][0] );
                TGraph* tge5 = new TGraph( lineList[2].size(), &lineList[2][0], &lineList[3][0] );
		
		char graphTitle1[256];
                sprintf(graphTitle1, "Fiducial Efficiency vs Rate for %s ROC %d DC %d", moduleName.c_str(), iRoc, use);
                TGE2->SetTitle(graphTitle1);
                TGE2->SetMarkerStyle(3);
                TGE2->SetMarkerSize(1);
                TGE2->GetXaxis()->SetTitle("Rate: MHz/cm^2");
                TGE2->GetYaxis()->SetTitle("Efficency 1.00 = 100%");
                TGE2->Draw("ap");

                tge4->SetMarkerColor( kRed );
                tge4->SetMarkerStyle(21);
 
                tge5->SetMarkerColor( kRed );
                tge5->SetMarkerStyle(21);

                TF1* myfit2 = new TF1("fitfun", "([0]-[1]*x*x*x)", 20, 140);
                myfit2->SetParameter(0, 1);
                myfit2->SetParLimits(0, 0.9, 1.1);
                myfit2->SetParameter(1, 5e-9);
                myfit2->SetParLimits(1, 1e-10, 5e-8);

                tge4->Draw("same");
                tge5->Draw("same");
                TGE2->Fit(myfit2, "BR");
                c3->Update();

                c3->Modified();
                gPad->Modified();
                char saveFileName1[256];
                sprintf(saveFileName1, "%s_Eff_C%d_DC%d.png",HighRateSaveFileName.c_str(), iRoc, use);
                c3->SaveAs(saveFileName1);
                c3->Clear();
                TGE2->Clear();

                myfit2->Clear();
                delete myfit2;
                delete c3;
*/
		dc = 0;
        	lowUni = 2.0;
        	highUni = 0.0;
        	lowUDC = 0;
        	highUDC = 0;
        	udceff = 0;
		
	}

        std::cout << "Working on Module" << endl;

	for( int i=0; i<nRocs; i++){
                for( int j=0; j<nDCol; j++){
                        totdc08 += dc08count[i][j];
                        totdc12 += dc12count[i][j];
                        totdc98 += dc98count[i][j];
                        totdc95 += dc95count[i][j];
			totdcboth += dcbothcount[i][j];
                }
        }
      	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*	TCanvas *c4 = new TCanvas("c1", "Efficiency", 200, 10, 700, 500);
        TGraphErrors* TGE = new TGraphErrors( efficiencies[nRocs].size(), &rates[nRocs][0], &efficiencies[nRocs][0], &rateErrors[nRocs][0], &efficiencyErrors[nRocs][0] );
        TGraph* tge2 = new TGraph( lineList[0].size(), &lineList[0][0], &lineList[1][0] );
        TGraph* tge3 = new TGraph( lineList[2].size(), &lineList[2][0], &lineList[3][0] );

	char graphTitle2[256];
        sprintf(graphTitle2, "%s Fiducial Efficiency vs Rate  for %s", HighRateFileName.c_str() , moduleName.c_str());
        TGE->SetTitle(graphTitle2);
	TGE->GetXaxis()->SetTitle("Rate: MHz/cm^2");
	TGE->GetYaxis()->SetTitle("Efficency 1.00 = 100%");
        TGE->SetMarkerStyle(7);
        TGE->SetMarkerSize(1);
        TGE->Draw("ap");


        tge2->SetMarkerColor(2 );
        tge2->SetMarkerStyle(21);

        tge3->SetMarkerColor(2 );
        tge3->SetMarkerStyle(21);

        TF1* myfit = new TF1("fitfun", "([0]-[1]*x*x*x)", 20, 140);
        myfit->SetParameter(0, 1);
        myfit->SetParLimits(0, 0.9, 1.1);
        myfit->SetParameter(1, 5e-9);
        myfit->SetParLimits(1, 1e-10, 5e-8);

        tge2->Draw("same");
        tge3->Draw("same");
        TGE->Fit(myfit, "BR");
        c4->Update();

        double p0= myfit->GetParameter(0);
        double p1= myfit->GetParameter(1);
        double p0_err = myfit->GetParError(0);
        double p1_err = myfit->GetParError(1);
        double eff_err = sqrt(p0_err * p0_err + pow(120.0,6) * p1_err * p1_err);
        
	outfile << (p0 - p1 * 120*120*120) << std::endl;
	log << endl;
        log << "Estimated Efficency at 120MHz/cm^2 : " << moduleName << " Eff: " << p0-p1 *120*120*120 << " +/- " << eff_err << endl;
	log << "Lowest DC Efficency at High Rate : ROC:" << lowestroc << " DC: " << lowestdc  << " Efficency: " << lowestdceff << endl;
	log << "Number DC <= 98% : " << totdc98 << endl;
	log << "Number DC <= 95% : " << totdc95 << endl;
	log << "Number DC >= 1.5 : " << totdc12 << endl;
        log << "Number DC <  0.6 : " << totdc08 << endl;
	log << "Number DC Both   : " << totdcboth << endl;
        c4->Modified();
      	gPad->Modified();
 	char saveFileName3[256];
  	sprintf(saveFileName3, "%s_Eff_%s.png",HighRateSaveFileName.c_str(), moduleName.c_str());
        c4->SaveAs(saveFileName3);
        c4->Clear();
        TGE->Clear();
        myfit->Clear();
       	delete myfit;
        delete c4;
*/	/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	for( int g = 0; g < DCUniNum.size(); g++){
		Uni.push_back( 10* ( DCUni[g] - phDCUni[g] ));
	}

	TCanvas *c5 = new TCanvas("c1", "DColUniformityComp", 200, 10, 700, 500);
        TGraph* tg4 = new TGraph( DCUniNum.size(), &DCUniNum[0], &Uni[0] );
	TGraph* tg6 = new TGraph( phDCUniNum.size(), &phDCUniNum[0], &phDCUni[0] );
        TGraph* tg2 = new TGraph( dclineList[0].size(), &dclineList[0][0], &dclineList[1][0] );
        TGraph* tg3 = new TGraph( dclineList[2].size(), &dclineList[2][0], &dclineList[3][0] );
	char graphTitle[256];
        sprintf(graphTitle, "%s DC Uniformity Comp for %s", HighRateFileName.c_str() , moduleName.c_str());
        tg4->SetTitle(graphTitle);
        tg4->GetXaxis()->SetTitle("DCol Number");
        tg4->GetYaxis()->SetTitle("DC Uniformity");
	tg4->GetYaxis()->SetRangeUser( 0.0, 2.0 );
	tg4->SetMarkerColor(kBlue);
        tg4->SetMarkerStyle(7);
        tg4->SetMarkerSize(1);
        tg4->Draw("apl");

	tg6->SetMarkerColor(kYellow);
	tg6->Draw("same");

        tg2->SetMarkerColor(kRed );
        tg2->SetMarkerStyle(21);
	tg2->Draw("same");

        tg3->SetMarkerColor(kRed );
        tg3->SetMarkerStyle(21);
        tg3->Draw("same");

        c5->Update();

        char saveFileName4[256];
        sprintf(saveFileName4, "%s_DC_Uniformity_Comp_%s.png",HighRateSaveFileName.c_str(), moduleName.c_str());
        c5->SaveAs(saveFileName4);
        c5->Clear();
        tg4->Clear();
	tg6->Clear();
	tg2->Clear();
	tg3->Clear();

        delete c5;
	delete tg4;
	delete tg6;
	delete tg2;
	delete tg3;

	////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*	TCanvas *c2 = new TCanvas("c2", "DColRate", 200, 10, 700, 500);
        TGraph* tg1 = new TGraph( dcolRates[nRocs][1].size(), &dcolRates[nRocs][1][0], &dcolRates[nRocs][0][0] );
        char graphTitle3[256];
        sprintf(graphTitle3, "%s Rate by DCol for %s", HighRateFileName.c_str() , moduleName.c_str());
        tg1->SetTitle(graphTitle3);
        tg1->GetXaxis()->SetTitle("DCol Number");
        tg1->GetYaxis()->SetTitle("Rate: MHa/cm^2");
        tg1->SetMarkerStyle(7);
        tg1->SetMarkerSize(1);
        tg1->Draw("ap");

        char saveFileName5[256];
        sprintf(saveFileName5, "%s_Rate_by_DCol_%s.png",HighRateSaveFileName.c_str(), moduleName.c_str());
        c2->SaveAs(saveFileName5);
        c2->Clear();
        tg1->Clear();
        delete c2;
*/	///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	outfile.close();
	system("rm -rf Auto*");
	std::cout <<"Thats all folks!!!" << endl; 
	return 0;


}

