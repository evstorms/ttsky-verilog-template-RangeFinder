module RangeFinder
   #(parameter WIDTH=16)
    (input  logic [WIDTH-1:0] data_in,
     input  logic             clock, reset,
     input  logic             go, finish,
     output logic [WIDTH-1:0] range,
     output logic             error);

   logic [WIDTH-1:0] high_q, low_q;
   logic run;

   always_ff @(posedge clock, posedge reset) begin
      if (reset) begin
         high_q <= 0;
         low_q <= 0;
         run <= 0;
         error <= 0;
         range <= 0;
      end
      else begin
         //error conditions
         if ((go && error) || (finish && ~run) || (go && run) ) begin
            error <= 1;
            run <= 0;
         end

         //go condition
         else if (go) begin
            high_q <= data_in;
            low_q <= data_in;
            run <= 1;
            error <=0;
         end
         
         //running condition
         if (run) begin
            if (data_in > high_q) high_q <= data_in;
            else if (data_in < low_q) low_q <= data_in;
         end

         //end condition
         if (finish) begin
            run <=0;
            range <= (high_q-low_q);
         end
      end
   end


endmodule: RangeFinder