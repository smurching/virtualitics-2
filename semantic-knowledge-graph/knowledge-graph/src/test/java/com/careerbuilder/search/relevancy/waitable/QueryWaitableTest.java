package com.careerbuilder.search.relevancy.waitable;

import com.careerbuilder.search.relevancy.NodeContext;
import mockit.Expectations;
import mockit.Mocked;
import mockit.integration.junit4.JMockit;
import org.apache.lucene.index.Term;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.TermQuery;
import org.apache.solr.search.DocSet;
import org.apache.solr.search.SolrIndexSearcher;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.IOException;

@RunWith(JMockit.class)
public class QueryWaitableTest
{

    NodeContext context;
    @Mocked SolrIndexSearcher searcher;
    @Mocked DocSet docSet;
    Query query;

    @Before
    public void init() throws IOException
    {
        context = new NodeContext();
        query = new TermQuery(new Term("testField1", "testQuery1"));

        new Expectations() {{
            searcher.numDocs(query, docSet); returns(1);
        }};
    }

    @Test
    public void call(){
        QueryWaitable target = new QueryWaitable(searcher, query, docSet, QueryWaitable.QueryType.FG, 1);

        target.call();

        Assert.assertEquals(1, target.result);
        Assert.assertEquals(QueryWaitable.QueryType.FG, target.type);
        Assert.assertEquals(1, target.index);
    }
}
