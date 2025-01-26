package main

import (
    "context"
    "fmt"
    "math/rand"
    "github.com/prometheus/prometheus/model/labels"
    "github.com/prometheus/prometheus/storage"
    "github.com/prometheus/prometheus/tsdb"
    "os"
    "time"
)

func main() {
    // Create a new TSDB instance
    db, err := tsdb.Open(
        "./src/data/prometheus", // directory where the data will be stored
        nil,      // a logger (can be nil for no logging)
        nil,      // an optional prometheus.Registerer
        tsdb.DefaultOptions(),
        nil,
	)

    if err != nil {
        fmt.Println("Error opening TSDB:", err)
        os.Exit(1)
    }
    defer db.Close()

    // Create a new appender
    app := db.Appender(context.Background())

    // Create labels for the gauge time series
    w1_label := labels.FromStrings(
	    "__name__", "washer 1", 
	    "type", "gauge",
	    "job", "synthetic",
	    "machine", "washer 1",
    )
    w2_label := labels.FromStrings(
	    "__name__", "washer 2", 
	    "type", "gauge",
	    "job", "synthetic",
	    "machine", "washer 2",
    )
    i1_label := labels.FromStrings(
	    "__name__", "ironer 1", 
	    "type", "gauge",
	    "job", "synthetic",
	    "machine", "ironer 1",
    )
    i2_label := labels.FromStrings(
	    "__name__", "ironer 2", 
	    "type", "gauge",
	    "job", "synthetic",
	    "machine", "ironer 2",
    )
    s1_label := labels.FromStrings(
	    "__name__", "small piece folder 1", 
	    "type", "gauge",
	    "job", "synthetic",
	    "machine", "small piece folder 1",
    )
    s2_label := labels.FromStrings(
	    "__name__", "small piece folder 2", 
	    "type", "gauge",
	    "job", "synthetic",
	    "machine", "small piece folder 2",
    )
    s3_label := labels.FromStrings(
	    "__name__", "small piece folder 3", 
	    "type", "gauge",
	    "job", "synthetic",
	    "machine", "small piece folder 3",
    )

    // Initialize a SeriesRef
    var ref storage.SeriesRef

    datapoints := 100
    rand.Seed(time.Now().UnixNano())

    washer_1_count := 0
    washer_2_count := 0
    ironer_1_count := 0
    ironer_2_count := 0
    small_piece_folder_1_count := 0
    small_piece_folder_2_count := 0
    small_piece_folder_3_count := 0

    washer_1_finished := true
    washer_2_finished := true
    ironer_1_finished := true
    ironer_2_finished := true
    small_piece_folder_1_finished := true
    small_piece_folder_2_finished := true
    small_piece_folder_3_finished := true
    
    for i := 0; i < datapoints; i++ {
        var err error

	washer_1 := rand.Intn(100) + 1
	washer_2 := rand.Intn(100) + 1
	ironer_1 := rand.Intn(100) + 1
	ironer_2 := rand.Intn(100) + 1
	small_piece_folder_1 := rand.Intn(100) + 1
	small_piece_folder_2 := rand.Intn(100) + 1
	small_piece_folder_3 := rand.Intn(100) + 1


	if washer_1  < 60 {
		washer_1_finished = true
	}
	if washer_2  < 60 {
		washer_2_finished = true
	}
	if ironer_1  < 20 {
		ironer_1_finished = true
	}
	if ironer_2  < 30 {
		ironer_2_finished = true
	}
	if small_piece_folder_1  < 10 {
		small_piece_folder_1_finished = true
	}
	if small_piece_folder_2  < 20 {
		small_piece_folder_2_finished = true
	}
	if small_piece_folder_3  < 30 {
		small_piece_folder_3_finished = true
	}
	// increment ironer 1
	if washer_1_finished && ironer_1_finished {
		ironer_1_count++
		fmt.Println("ironer_1_count", ironer_1_count)
		ref, err = app.Append(
			ref, 
			i1_label, 
			( time.Now().Unix() - (14 * 24 * 60 * 60) + (60 * int64(i)) ) * 1000, 
			float64(ironer_1_count),
		)
		ironer_1_finished = false
		washer_1_finished = false
		if err != nil {
		    fmt.Println("error appending ironer 1:", err)
		    os.Exit(1)
		}
	}
	// increment ironer 2
	if washer_2_finished && ironer_2_finished {
		ironer_2_count++
		ref, err = app.Append(
			ref, 
			i2_label, 
			( time.Now().Unix() - (14 * 24 * 60 * 60) + (60 * int64(i)) ) * 1000, 
			float64(ironer_2_count),
		)
		ironer_2_finished = false
		washer_2_finished = false
		if err != nil {
		    fmt.Println("error appending ironer 2:", err)
		    os.Exit(1)
		}
	}
	// increment small piece folder 1
	if washer_1_finished && small_piece_folder_1_finished {
		small_piece_folder_1_count++
		ref, err = app.Append(
			ref, 
			s1_label, 
			( time.Now().Unix() - (14 * 24 * 60 * 60) + (60 * int64(i)) ) * 1000, 
			float64(small_piece_folder_1_count),
		)
		small_piece_folder_1_finished = false
		washer_1_finished = false
		if err != nil {
		    fmt.Println("error appending spf 1:", err)
		    os.Exit(1)
		}
	}
	// increment small piece folder 2
	if washer_1_finished && small_piece_folder_2_finished {
		small_piece_folder_2_count++
		ref, err = app.Append(
			ref, 
			s2_label, 
			( time.Now().Unix() - (14 * 24 * 60 * 60) + (60 * int64(i)) ) * 1000, 
			float64(small_piece_folder_2_count),
		)
		small_piece_folder_2_finished = false
		washer_1_finished = false
		if err != nil {
		    fmt.Println("error appending spf 2:", err)
		    os.Exit(1)
		}
	}
	// increment small piece folder 3
	if washer_2_finished && small_piece_folder_3_finished {
		small_piece_folder_3_count++
		ref, err = app.Append(
			ref, 
			s3_label, 
			( time.Now().Unix() - (14 * 24 * 60 * 60) + (60 * int64(i)) ) * 1000, 
			float64(small_piece_folder_3_count),
		)
		small_piece_folder_3_finished = false
		washer_2_finished = false
		if err != nil {
		    fmt.Println("error appending spf 3:", err)
		    os.Exit(1)
		}
	}
	// increment washer 1
	if washer_1_finished {
		washer_1_count++
		ref, err = app.Append(
			ref, 
			w1_label, 
			( time.Now().Unix() - (14 * 24 * 60 * 60) + (60 * int64(i)) ) * 1000, 
			float64(washer_1_count),
		)
		washer_1_finished = false
		if err != nil {
		    fmt.Println("error appending washer 1:", err)
		    os.Exit(1)
		}
	}
	// increment washer 2
	if washer_2_finished {
		washer_2_count++
		ref, err = app.Append(
			ref, 
			w2_label, 
			( time.Now().Unix() - (14 * 24 * 60 * 60) + (60 * int64(i)) ) * 1000, 
			float64(washer_2_count),
		)
		washer_2_finished = false
		if err != nil {
		    fmt.Println("error appending washer 2:", err)
		    os.Exit(1)
		}
	}

    }

    // Commit the data
    err = app.Commit()
    if err != nil {
        fmt.Println("Error committing:", err)
        os.Exit(1)
    }

    // Compact the TSDB
    if err := db.Compact(context.Background()); err != nil {
    	fmt.Println("error compacting TSDB: ", err)
        os.Exit(1)
    }
}
