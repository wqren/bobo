function [bbox, is_occluded] = videobbox(indir, n_imskip, outfile)
%--------------------------------------------------------------------------
%
% Copyright (c) 2012 Jeffrey Byrne
%
%--------------------------------------------------------------------------


%% Input
imlist = bobo.util.imlist(indir);
if nargin < 3
  outfile = 'annotation.mat';
end


%% Video bounding box annotation!
global GUI;  % usage annotation
GUI.imlist = imlist;
GUI.startframe = 1;
GUI.currentframe = 1;
GUI.endframe = length(imlist);
GUI.skipframe = n_imskip;
if exist(outfile, 'file')
  mat = load(outfile);
  GUI.bbox = mat.bbox;  % initialize 
  GUI.is_occluded = mat.is_occluded;  % initialize 
end
gui_videobbox();  % ${BOBO}/matlab/gui


%% Output
bbox = GUI.bbox;  % [x y w h] format
is_occluded = GUI.is_occluded;  % binary 
save(outfile,'imlist','bbox','is_occluded');
fprintf('[%s]: exporting to ''%s''\n', mfilename, outfile);
