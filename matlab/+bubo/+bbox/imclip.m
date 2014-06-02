function [bb] = imclip(im, bb)
%--------------------------------------------------------------------------
%
% Copyright (c) 2014 Jeffrey Byrne
%
%--------------------------------------------------------------------------


bb(:,1) = max(bb(:,1), 1);
bb(:,2) = max(bb(:,2), 1);
bb(:,3) = min(bb(:,3), size(im, 2));
bb(:,4) = min(bb(:,4), size(im, 1));
