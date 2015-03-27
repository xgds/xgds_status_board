// __BEGIN_LICENSE__
//Copyright © 2015, United States Government, as represented by the 
//Administrator of the National Aeronautics and Space Administration. 
//All rights reserved.
//
//The xGDS platform is licensed under the Apache License, Version 2.0 
//(the "License"); you may not use this file except in compliance with the License. 
//You may obtain a copy of the License at 
//http://www.apache.org/licenses/LICENSE-2.0.
//
//Unless required by applicable law or agreed to in writing, software distributed 
//under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
//CONDITIONS OF ANY KIND, either express or implied. See the License for the 
//specific language governing permissions and limitations under the License.
// __END_LICENSE__

Date.prototype.setISO8601 = function(dString) {

var regexp = /(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)(\.\d+)?(Z|([+-])(\d\d)(:)?(\d\d))/;

if (dString.toString().match(new RegExp(regexp))) {
var d = dString.match(new RegExp(regexp));
var offset = 0;

this.setUTCDate(1);
this.setUTCFullYear(parseInt(d[1], 10));
this.setUTCMonth(parseInt(d[3], 10) - 1);
this.setUTCDate(parseInt(d[5], 10));
this.setUTCHours(parseInt(d[7], 10));
this.setUTCMinutes(parseInt(d[9], 10));
this.setUTCSeconds(parseInt(d[11], 10));
if (d[12])
this.setUTCMilliseconds(parseFloat(d[12]) * 1000);
else
this.setUTCMilliseconds(0);
if (d[13] != 'Z') {
offset = (d[15] * 60) + parseInt(d[17], 10);
offset *= ((d[14] == '-') ? -1 : 1);
this.setTime(this.getTime() - offset * 60 * 1000);
}
}
else {
this.setTime(Date.parse(dString));
}
return this;
};
