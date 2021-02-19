#!/usr/bin/env ruby

require 'json'
require 'optparse'
#require 'pry'


class Terrain
  class Water
    def self.char()
      "~"
    end

    def self.color()
      "\033[34m"
    end
  end

  class Ground
    def self.char()
      "G"
    end

    def self.color()
      "\033[32m"
    end
  end

  class Mountain
    def self.char()
      "^"
    end

    def self.color()
      "\033[31m"
    end
  end

  class Forest
    def self.char()
      "F"
    end

    def self.color()
      "\033[33m"
    end
  end
end

class Map
  attr_accessor :grid, :seed

  def initialize(height, width, seed)
    @grid = []
    @seed = seed
    @height = height
    @width = width

    @height.times do |n|
      row = []
      @width.times do |m|
        row << Cell.new(m, n, Terrain::Water)
      end
      @grid[n] = row
    end
  end

  def render()
    @grid.reverse.each do |row|
      row.each do |cell|
        print cell.render()
      end

      puts
    end
  end

  def render_json()
    @grid.reverse.each_with_index do |row,i|
      tmp = []
      row.each_with_index do |cell,j|
        tmp << cell.terrain.char
      end
      @grid[i] = tmp
    end

    map = {
      "seed" => @seed,
      "grid" => @grid,
    }

    puts JSON.pretty_generate(map)
  end

  def cell(x, y)
    if(@grid[y])
      return @grid[y][x]
    else
      return nil
    end
  end
  
  def north_of(x, y)
    cell(x, y+1)
  end
  
  def northeast_of(x, y)
    cell(x+1, y+1)
  end
  
  def east_of(x, y)
    cell(x+1, y)
  end
  
  def southeast_of(x, y)
    cell(x+1, y-1)
  end
  
  def south_of(x, y)
    cell(x, y-1)
  end
  
  def southwest_of(x, y)
    cell(x-1, y-1)
  end
  
  def west_of(x, y)
    cell(x-1, y)
  end
  
  def northwest_of(x, y)
    cell(x-1, y+1)
  end
end

class Cell
  attr_accessor :x, :y, :terrain

  def initialize(x, y, terrain)
    @x = x
    @y = y
    @terrain = terrain
  end

  def render()
    return " #{terrain.color}#{terrain.char}\033[00m"
  end
end

def generate_map(height, width, config, iteration_order, seed)
  map = Map.new(height, width, seed)

  map = generate_land(map, config["land"], iteration_order)
  map = generate_mountains(map, config["mountain"], iteration_order)
  map = generate_forests(map, config["forest"], iteration_order)

  return map
end

def generate_land(map, config, iteration_order)
  iteration_order.each do |coord|
    x, y = coord

    likelihood = config["base-percentage"]
    likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.north_of(x, y) && map.north_of(x, y).terrain == Terrain::Ground
    likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.south_of(x, y) && map.south_of(x, y).terrain == Terrain::Ground
    likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.west_of(x, y) && map.west_of(x, y).terrain == Terrain::Ground
    likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.east_of(x, y) && map.east_of(x, y).terrain == Terrain::Ground
    likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northeast_of(x, y) && map.northeast_of(x, y).terrain == Terrain::Ground
    likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southeast_of(x, y) && map.southeast_of(x, y).terrain == Terrain::Ground
    likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southwest_of(x, y) && map.southwest_of(x, y).terrain == Terrain::Ground
    likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northwest_of(x, y) && map.northwest_of(x, y).terrain == Terrain::Ground

    if rand(config["max-likelihood"]) < likelihood
      map.cell(x, y).terrain = Terrain::Ground
    end
  end

  return map
end

def generate_mountains(map, config, iteration_order)
  iteration_order.each do |coord|
    x, y = coord

    if map.cell(x, y).terrain != Terrain::Water
      likelihood = config["base-percentage"]
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.north_of(x, y) && map.north_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.south_of(x, y) && map.south_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.east_of(x, y) && map.east_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.west_of(x, y) && map.west_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northeast_of(x, y) && map.northeast_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southeast_of(x, y) && map.southeast_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southwest_of(x, y) && map.southwest_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northwest_of(x, y) && map.northwest_of(x, y).terrain == Terrain::Mountain

      if rand(config["max-likelihood"]) < likelihood
        map.cell(x, y).terrain = Terrain::Mountain
      end
    end
  end

  return map
end

def generate_forests(map, config, iteration_order)
  iteration_order.each do |coord|
    x, y = coord
    if ![Terrain::Water, Terrain::Mountain].include?(map.cell(x, y))
      likelihood = config["base-percentage"]
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.north_of(x, y) && map.north_of(x, y).terrain == Terrain::Forest
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.south_of(x, y) && map.south_of(x, y).terrain == Terrain::Forest
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.east_of(x, y) && map.east_of(x, y).terrain == Terrain::Forest
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.west_of(x, y) && map.west_of(x, y).terrain == Terrain::Forest
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northeast_of(x, y) && map.northeast_of(x, y).terrain == Terrain::Forest
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southeast_of(x, y) && map.southeast_of(x, y).terrain == Terrain::Forest
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southwest_of(x, y) && map.southwest_of(x, y).terrain == Terrain::Forest
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northwest_of(x, y) && map.northwest_of(x, y).terrain == Terrain::Forest

      likelihood = likelihood + config["mountain-adjacency-add-percentage"] if map.north_of(x, y) && map.north_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["mountain-adjacency-add-percentage"] if map.south_of(x, y) && map.south_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["mountain-adjacency-add-percentage"] if map.east_of(x, y) && map.east_of(x, y).terrain == Terrain::Mountain
      likelihood = likelihood + config["mountain-adjacency-add-percentage"] if map.west_of(x, y) && map.west_of(x, y).terrain == Terrain::Mountain

      likelihood = likelihood - config["water-adjacency-subtract-percentage"] if map.north_of(x, y) && map.north_of(x, y).terrain == Terrain::Water
      likelihood = likelihood - config["water-adjacency-subtract-percentage"] if map.south_of(x, y) && map.south_of(x, y).terrain == Terrain::Water
      likelihood = likelihood - config["water-adjacency-subtract-percentage"] if map.east_of(x, y) && map.east_of(x, y).terrain == Terrain::Water
      likelihood = likelihood - config["water-adjacency-subtract-percentage"] if map.west_of(x, y) && map.west_of(x, y).terrain == Terrain::Water

      if rand(config["max-likelihood"]) < likelihood
        map.cell(x, y).terrain = Terrain::Forest
      end
    end
  end

  return map
end

def get_iteration_order(type, grid_height, grid_width)
  coords_list = []

  grid_height.times do |n|
    grid_width.times do |m|
      coords_list << [m,n]
    end
  end

  if type == "standard"
    # do nothing
  elsif type == "shuffle"
    coords_list.shuffle!
  end

  return coords_list
end


options = {}
OptionParser.new do |opts|
  opts.banner = 'generate_map.rb [dimensions] [config_file_path] [seed] [--json]\n'\
                'Example: generate_map.rb 64x64 config/standard-map.json 1235\n\n'\

  opts.on("-j", "--json", "Dump map as json") do |j|
    options[:json] = j
  end
end.parse!

map_height, map_width = ARGV[0].split("x").collect{|d| d.to_i}

config_file_path = ARGV[1]
file_contents = File.read(config_file_path)
config = JSON.parse(file_contents)

seed = (ARGV[2] || rand(1000000000)).to_i
srand(seed)

map = generate_map(map_height, map_width, config, get_iteration_order(config["iteration_type"], map_height, map_width), seed)

if !options[:json]
  map.render()

  puts "Config: #{config_file_path}"
  puts "Dimensions: #{map_height}x#{map_width}"
  puts "Seed: #{seed}"
else
  map.render_json()
end
