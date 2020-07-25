#!/usr/bin/env ruby

#grid = [["(0,0)","(0,1)","(0,2)","(0,3)"],["(1,0)","(1,1)","(1,2)","(1,3)"],["(2,0)","(2,1)","(2,2)","(2,3)"],["(3,0)","(3,1)","(3,2)","(3,3)"]]
class Map
    attr_accessor :grid
    
    def initialize(height, width)
        @grid = []

        height.times do |n|
            row = []
            width.times do |m|
                row << [m,n]
            end
            @grid[n] = row
        end
    end

    def cell(x, y)
        @grid[y][x]
    end

    def render()
        @grid.reverse.each do |r|
            r.each do |c|
                print " (#{c.join(",")})"
            end
            print "\n\n"
        end
    end
end

def mirror_grid_position(grid_height, grid_width, x, y)
    return (grid_height - 1) - x, (grid_width - 1) - y
end

grid = Map.new(8, 8)
grid.render

pp grid.cell(0,0)
pp grid.cell(1,3)




# pp(mirror_grid_position(4,4,0,0))
# pp(mirror_grid_position(4,4,3,3))
# pp(mirror_grid_position(4,4,1,0))
# pp(mirror_grid_position(4,4,0,1))
# pp(mirror_grid_position(4,4,1,1))
# pp(mirror_grid_position(4,4,0,3))

def pp(cell)
    puts "(#{cell.join(",")})"
end